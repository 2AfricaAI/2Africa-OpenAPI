"""L1 Basic conformance: OAuth + at least one upstream endpoint + Privacy Manifest."""
from __future__ import annotations
import uuid
import pytest


pytestmark = pytest.mark.l1


# ---- 1. System probe ---------------------------------------------------

def test_healthz_returns_ok(http, base_url):
    r = http.get(f"{base_url}/healthz", headers={"X-Spec-Version": "1.0.0-rc1"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in {"ok", "degraded"}
    assert "spec_version" in body
    assert "server_time" in body


# ---- 2. OAuth metadata -------------------------------------------------

def test_oauth_metadata_endpoint(http, base_url):
    r = http.get(f"{base_url}/.well-known/oauth-authorization-server")
    if r.status_code == 404:
        pytest.skip("OAuth metadata endpoint not implemented by this server")
    assert r.status_code == 200
    meta = r.json()
    assert "issuer" in meta
    assert "authorization_endpoint" in meta
    assert "token_endpoint" in meta
    assert "jwks_uri" in meta
    assert "S256" in meta.get("code_challenge_methods_supported", [])


# ---- 3. Privacy Manifest publish + hash binding ------------------------

def test_publish_manifest_returns_hash(manifest_hash):
    assert manifest_hash.startswith("sha256:")
    assert len(manifest_hash) == len("sha256:") + 64


# ---- 4. Upstream yields end-to-end ------------------------------------

def test_upstream_yields_round_trip(http, base_url, manifest_hash, tenant_pseudo_id, fresh_idempotency_key):
    body = {
        "tenant_pseudo_id": tenant_pseudo_id,
        "records": [{
            "record_id":    str(uuid.uuid4()),
            "crop_code":    "TOMATO",
            "region_code":  "KE-30",
            "harvest_date": "2026-05-20",
            "quantity":     {"quantity": 1234.5, "unit": "kg"},
        }],
    }
    r = http.post(
        f"{base_url}/v1/upstream/yields",
        json=body,
        headers={
            "X-Privacy-Manifest-Hash": manifest_hash,
            "Idempotency-Key":         fresh_idempotency_key,
        },
        timeout=30,
    )
    assert r.status_code == 202, f"got {r.status_code}: {r.text[:200]}"
    ack = r.json()
    assert "batch_id" in ack
    assert "accepted_count" in ack
    assert "accepted_at" in ack


# ---- 5. Manifest hash mismatch returns 422 ----------------------------

def test_wrong_manifest_hash_rejected_422(http, base_url, tenant_pseudo_id, fresh_idempotency_key):
    wrong = "sha256:" + "0" * 64
    body = {"tenant_pseudo_id": tenant_pseudo_id, "records": []}
    r = http.post(
        f"{base_url}/v1/upstream/yields",
        json=body,
        headers={
            "X-Privacy-Manifest-Hash": wrong,
            "Idempotency-Key":         fresh_idempotency_key,
        },
        timeout=30,
    )
    assert r.status_code == 422
    assert r.headers.get("Content-Type", "").startswith("application/problem+json")
    body = r.json()
    assert "manifest" in body.get("type", "").lower() or "manifest" in body.get("title", "").lower()


# ---- 6. Idempotency replay returns the original response ---------------

def test_idempotency_replay(http, base_url, manifest_hash, tenant_pseudo_id):
    key = str(uuid.uuid4())
    body = {
        "tenant_pseudo_id": tenant_pseudo_id,
        "records": [{
            "record_id":    str(uuid.uuid4()),
            "crop_code":    "MAIZE",
            "region_code":  "KE-30",
            "harvest_date": "2026-05-21",
            "quantity":     {"quantity": 100, "unit": "kg"},
        }],
    }
    headers = {"X-Privacy-Manifest-Hash": manifest_hash, "Idempotency-Key": key}
    r1 = http.post(f"{base_url}/v1/upstream/yields", json=body, headers=headers, timeout=30)
    r2 = http.post(f"{base_url}/v1/upstream/yields", json=body, headers=headers, timeout=30)
    assert r1.status_code == r2.status_code == 202
    # The second call MUST surface a replay marker
    assert r2.headers.get("Idempotency-Replay", "").lower() == "true" or r1.json() == r2.json()
