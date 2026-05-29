"""Shared fixtures for the CTS pytest runner.

Configure via env:
    CTS_BASE_URL           - target server, e.g. https://sandbox.agricloud.2africa.ai
    CTS_ACCESS_TOKEN       - JWT access token with all upstream/downstream scopes
    CTS_MANIFEST_PATH      - path to the Privacy Manifest YAML to publish
    CTS_TENANT_PSEUDO_ID   - UUID v4 (defaults to a fixed test id)
    CTS_WEBHOOK_SECRET     - shared secret for webhook signature tests
"""
from __future__ import annotations
import os, sys, pathlib, uuid
from typing import Optional

import pytest
import requests

SPEC_VERSION = "1.0.0-rc1"
DEFAULT_TENANT = "f47ac10b-58cc-4372-a567-0e02b2c3d479"


def _require_env(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        pytest.skip(f"{name} not set; skipping live test")
    return val


@pytest.fixture(scope="session")
def base_url() -> str:
    return _require_env("CTS_BASE_URL").rstrip("/")


@pytest.fixture(scope="session")
def access_token() -> str:
    return _require_env("CTS_ACCESS_TOKEN")


@pytest.fixture(scope="session")
def tenant_pseudo_id() -> str:
    return os.environ.get("CTS_TENANT_PSEUDO_ID", DEFAULT_TENANT)


@pytest.fixture(scope="session")
def http(base_url, access_token) -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "Authorization": f"Bearer {access_token}",
        "X-Spec-Version": SPEC_VERSION,
    })
    return s


@pytest.fixture(scope="session")
def manifest_yaml() -> str:
    p = os.environ.get("CTS_MANIFEST_PATH")
    if not p:
        # Fallback: balanced preset bundled with the spec repo
        repo_root = pathlib.Path(__file__).resolve().parents[3]
        p = repo_root / "examples" / "manifests" / "balanced.yaml"
    return pathlib.Path(p).read_text()


@pytest.fixture(scope="session")
def manifest_hash(http, base_url, manifest_yaml) -> str:
    """Publish the manifest and cache the returned hash for the whole session."""
    r = http.put(
        f"{base_url}/v1/privacy-manifest",
        data=manifest_yaml.encode("utf-8"),
        headers={
            "Content-Type": "application/yaml",
            "Idempotency-Key": str(uuid.uuid4()),
        },
        timeout=30,
    )
    assert r.status_code == 200, f"Manifest publish failed: {r.status_code} {r.text[:200]}"
    body = r.json()
    return body["manifest_hash"]


@pytest.fixture
def fresh_idempotency_key() -> str:
    return str(uuid.uuid4())
