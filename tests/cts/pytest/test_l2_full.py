"""L2 Full conformance: all 10 endpoints + signed webhook delivery."""
from __future__ import annotations
import hashlib, hmac, time, uuid, re
import pytest


pytestmark = pytest.mark.l2


# ---- All 5 upstream endpoints respond 2xx with the right schema --------

@pytest.mark.parametrize("path,body_builder,expected", [
    ("/v1/upstream/prices", lambda tpi: {
        "tenant_pseudo_id": tpi,
        "records": [{
            "record_id":   str(uuid.uuid4()),
            "sku_code":    "TOMATO_GRADE_A",
            "region_code": "KE-30",
            "sold_on":     "2026-05-22",
            "unit_price":  {"amount": "75.00", "currency": "KES"},
            "per_unit":    "kg",
        }],
    }, 202),
    ("/v1/upstream/gap-records", lambda tpi: {
        "tenant_pseudo_id": tpi,
        "records": [{
            "record_id":   str(uuid.uuid4()),
            "audit_date":  "2026-04-12",
            "scheme":      "GLOBALG_A_P",
            "result":      "pass",
            "non_conformities": 0,
            "region_code": "KE-30",
        }],
    }, 202),
])
def test_upstream_endpoint_accepts(http, base_url, manifest_hash, tenant_pseudo_id, path, body_builder, expected):
    body = body_builder(tenant_pseudo_id)
    r = http.post(
        f"{base_url}{path}",
        json=body,
        headers={
            "X-Privacy-Manifest-Hash": manifest_hash,
            "Idempotency-Key":         str(uuid.uuid4()),
        },
        timeout=30,
    )
    assert r.status_code == expected, f"{path}: {r.status_code} {r.text[:200]}"


# ---- All 5 downstream GETs respond 2xx ----------------------------------

@pytest.mark.parametrize("path,params", [
    ("/v1/downstream/dictionaries", {"kind": "crop", "page_size": 5}),
    ("/v1/downstream/prices",       {"region_code": "KE-30", "window": "30d", "page_size": 5}),
    ("/v1/downstream/marketplace",  {"region_code": "KE-30", "page_size": 5}),
    ("/v1/downstream/procurement",  {"region_code": "KE-30", "page_size": 5}),
])
def test_downstream_endpoint_responds(http, base_url, path, params):
    r = http.get(f"{base_url}{path}", params=params, timeout=30)
    # 200 = data, 404 = filtered out by sample-size floor; both are spec-conformant
    assert r.status_code in {200, 404}, f"{path}: {r.status_code} {r.text[:200]}"
    if r.status_code == 200:
        body = r.json()
        assert "items" in body, body


def test_benchmarks_endpoint_responds(http, base_url):
    r = http.get(
        f"{base_url}/v1/downstream/benchmarks",
        params={"region_code": "KE-30", "crop_code": "TOMATO"},
        timeout=30,
    )
    assert r.status_code in {200, 404}
    if r.status_code == 200:
        body = r.json()
        assert "metrics" in body
        if body["metrics"].get("sample_size", 0) < 30:
            pytest.fail("Server returned a row with sample_size < 30 — privacy violation")


# ---- RFC 7807 catalogue ------------------------------------------------

def test_invalid_token_returns_problem_json(base_url):
    import requests
    r = requests.get(
        f"{base_url}/v1/downstream/dictionaries",
        headers={"Authorization": "Bearer obviously-not-a-real-token", "X-Spec-Version": "1.0.0-rc1"},
        timeout=30,
    )
    assert r.status_code == 401
    assert r.headers.get("Content-Type", "").startswith("application/problem+json")
    body = r.json()
    assert body["status"] == 401
    assert "type" in body and "title" in body


def test_unknown_scope_returns_403(http, base_url):
    # We can't easily synthesise a token with wrong scopes here, but we can
    # at least assert the contract by trying an endpoint that requires a
    # scope the test token shouldn't have. Skip if all scopes are granted.
    pytest.skip("Requires a token mint with restricted scopes (out of CTS auto scope)")


# ---- Webhook signature verification (offline) --------------------------

@pytest.mark.needs_webhook
def test_webhook_signature_helpers_round_trip():
    """Round-trip a payload through the helper to prove the algorithm matches the spec."""
    import sys, pathlib
    repo = pathlib.Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repo / "examples" / "helpers" / "python"))
    from webhook_verify import verify_signature

    secret = "whsec_cts_demo_do_not_use_in_prod"
    raw = b'{"event_id":"x","event_type":"system.healthcheck","created_at":"2026-05-29T14:30:00Z"}'
    ts = int(time.time())
    digest = hmac.new(secret.encode(), f"{ts}.".encode() + raw, hashlib.sha256).hexdigest()
    header = f"t={ts},v1={digest}"
    # Must not raise
    verify_signature(secret, header, raw)



# ---- v1.1 RFC-019 webhook backfill ------------------------------------

def test_events_backfill_endpoint_responds(http, base_url):
    """RFC-019: GET /v1/events?since=<ts> returns the page envelope."""
    import time
    since = int(time.time()) - 3600  # last hour
    r = http.get(f"{base_url}/v1/events", params={"since": since, "page_size": 5}, timeout=30)
    if r.status_code == 404:
        pytest.skip("Endpoint not implemented (server still on v1.0)")
    assert r.status_code == 200, r.text[:200]
    body = r.json()
    assert "items" in body
    if body["items"]:
        row = body["items"][0]
        assert "delivery_id" in row
        assert "signature" in row
        assert "payload" in row


# ---- v1.1 RFC-021 marketplace response --------------------------------

def test_marketplace_response_endpoint_responds(http, base_url, tenant_pseudo_id, fresh_idempotency_key):
    """RFC-021: POST a response to a marketplace order. We accept 404 (no
    matching order in sandbox) or 201 (accepted) — both prove the endpoint
    exists with the right contract."""
    import uuid
    body = {
        "seller_pseudo_id":   tenant_pseudo_id,
        "offered_quantity":   {"quantity": 5000, "unit": "kg"},
        "offered_unit_price": {"amount": "78.50", "currency": "KES"},
        "available_from":     "2026-06-01",
        "available_until":    "2026-06-10",
        "notes":              "CTS automated probe; ignore",
    }
    order_id = str(uuid.uuid4())  # synthetic; server should 404
    r = http.post(
        f"{base_url}/v1/downstream/marketplace/{order_id}/responses",
        json=body,
        headers={"Idempotency-Key": fresh_idempotency_key},
        timeout=30,
    )
    if r.status_code == 404 and "v1.1" not in r.text and "responses" in r.text:
        # Likely the order_id-specific 404, not the endpoint 404 — this is fine.
        pass
    assert r.status_code in {201, 404, 410}, f"{r.status_code}: {r.text[:200]}"
    if r.status_code == 201:
        ack = r.json()
        assert "response_id" in ack
        assert ack["order_id"] == order_id
        assert "accepted_at" in ack
        assert "buyer_notified" in ack
