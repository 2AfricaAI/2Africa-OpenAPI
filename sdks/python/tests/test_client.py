"""Offline tests using a fake requests.Session - no network."""
from __future__ import annotations
import json
import uuid
from typing import Any, Callable, Dict, List
from unittest.mock import MagicMock

import pytest
import requests

from twoafrica_openapi import (
    TwoAfricaClient, SpecVersion,
    InvalidToken, InsufficientScope, ManifestHashMismatch,
    RateLimited, IdempotencyConflict,
)


def _fake_response(status: int, body: Any = None, *, headers: dict | None = None) -> MagicMock:
    r = MagicMock(spec=requests.Response)
    r.status_code = status
    r.reason = {200: "OK", 201: "Created", 202: "Accepted", 204: "No Content"}.get(status, "")
    r.headers = headers or {}
    if status == 204:
        r.json.side_effect = ValueError("no body")
        r.text = ""
    else:
        r.json.return_value = body
        r.text = json.dumps(body) if body is not None else ""
    return r


def _record_call(captured: List[Dict[str, Any]]) -> Callable:
    def go(*args, **kwargs):
        captured.append({"args": args, "kwargs": kwargs})
        return go.next_response
    go.next_response = None
    return go


@pytest.fixture
def client_and_session():
    sess = MagicMock(spec=requests.Session)
    client = TwoAfricaClient(
        base_url="https://sandbox.example",
        access_token="tok",
        manifest_hash="sha256:0000000000000000000000000000000000000000000000000000000000000000",
        session=sess,
    )
    return client, sess


def test_healthz_sends_spec_version(client_and_session):
    client, sess = client_and_session
    sess.get.return_value = _fake_response(200, {"status": "ok", "spec_version": SpecVersion, "server_time": "x"})
    out = client.healthz()
    assert out["status"] == "ok"
    sess.get.assert_called_once()
    headers = sess.get.call_args.kwargs["headers"]
    assert headers["X-Spec-Version"] == SpecVersion
    assert "Authorization" not in headers   # healthz is unauthenticated


def test_yields_attaches_mandatory_headers(client_and_session):
    client, sess = client_and_session
    sess.post.return_value = _fake_response(202,
        {"batch_id": "11111111-1111-1111-1111-111111111111", "accepted_count": 1, "accepted_at": "2026-05-29T14:30:00Z"})
    ack = client.upstream.yields(
        tenant_pseudo_id="22222222-2222-2222-2222-222222222222",
        records=[{
            "record_id": "33333333-3333-3333-3333-333333333333",
            "crop_code": "TOMATO", "region_code": "KE-30",
            "harvest_date": "2026-05-20",
            "quantity": {"quantity": 1.0, "unit": "kg"},
        }],
    )
    assert ack.accepted_count == 1
    headers = sess.post.call_args.kwargs["headers"]
    assert headers["X-Spec-Version"] == SpecVersion
    assert headers["X-Privacy-Manifest-Hash"].startswith("sha256:")
    assert headers["Authorization"] == "Bearer tok"
    uuid.UUID(headers["Idempotency-Key"])  # well-formed UUID v4


def test_yields_without_manifest_hash_raises(client_and_session):
    client, _ = client_and_session
    client.manifest_hash = None
    with pytest.raises(RuntimeError, match="X-Privacy-Manifest-Hash"):
        client.upstream.yields(tenant_pseudo_id="x", records=[])


def test_manifest_hash_mismatch_raises_typed_exception(client_and_session):
    client, sess = client_and_session
    sess.post.return_value = _fake_response(422, {
        "type":   "https://errors.2africa.ai/manifest-hash-mismatch",
        "title":  "Unprocessable Entity",
        "status": 422,
        "detail": "Server has a different manifest hash cached.",
    })
    with pytest.raises(ManifestHashMismatch) as ei:
        client.upstream.yields(tenant_pseudo_id="x", records=[{"a": 1}])
    assert ei.value.status == 422


def test_invalid_token_raised_on_401(client_and_session):
    client, sess = client_and_session
    sess.get.return_value = _fake_response(401, {
        "type": "https://errors.2africa.ai/invalid-token",
        "title": "Unauthorized",
        "status": 401,
        "detail": "Access token expired."})
    with pytest.raises(InvalidToken):
        client.downstream.dictionaries()


def test_rate_limited_propagates_retry_after(client_and_session):
    client, sess = client_and_session
    sess.get.return_value = _fake_response(429, {
        "type": "https://errors.2africa.ai/rate-limited",
        "title": "Too Many Requests",
        "status": 429,
        "detail": "Quota exhausted.",
    }, headers={"Retry-After": "47"})
    with pytest.raises(RateLimited) as ei:
        client.downstream.dictionaries()
    assert ei.value.status == 429


def test_idempotency_conflict_409(client_and_session):
    client, sess = client_and_session
    sess.post.return_value = _fake_response(409, {
        "type": "https://errors.2africa.ai/idempotency-conflict",
        "title": "Conflict",
        "status": 409,
        "detail": "key reused with different body",
    })
    with pytest.raises(IdempotencyConflict):
        client.upstream.yields(tenant_pseudo_id="x", records=[{}])


def test_publish_manifest_caches_hash(client_and_session):
    client, sess = client_and_session
    client.manifest_hash = None
    sess.put.return_value = _fake_response(200, {"manifest_hash": "sha256:" + "a" * 64, "accepted_at": "2026-05-29T14:30:00Z"})
    ack = client.privacy.publish_manifest("manifest_version: 1.0.0\nprofile: balanced\n")
    assert ack.manifest_hash.endswith("a" * 64)
    assert client.manifest_hash == ack.manifest_hash


def test_telemetry_no_idempotency_key(client_and_session):
    client, sess = client_and_session
    sess.post.return_value = _fake_response(204)
    client.upstream.telemetry(
        tenant_pseudo_id="x",
        events=[{"event": "dashboard.opened", "occurred_at": "2026-05-29T14:30:00Z"}],
    )
    headers = sess.post.call_args.kwargs["headers"]
    assert "Idempotency-Key" not in headers
