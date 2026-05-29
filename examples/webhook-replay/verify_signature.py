#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
# SPDX-License-Identifier: Apache-2.0
"""
Reference HMAC-SHA256 verifier for 2Africa OpenAPI webhooks.

    X-AgriCloud-Signature: t=<unix>,v1=<hex>
    secret_key = the value provisioned at subscription time
    HMAC body  = f"{t}.{raw_body}".encode("utf-8")

Reject if:
  - signature header malformed
  - timestamp differs from now() by more than 300 seconds (replay)
  - computed HMAC != supplied HMAC (constant-time compare)

Typical usage in a Flask/Starlette handler:

    raw = request.get_data()   # MUST be the raw bytes, before parsing
    verify_signature(
        secret    = os.environ["WEBHOOK_SECRET"],
        header    = request.headers["X-AgriCloud-Signature"],
        raw_body  = raw,
    )
"""
from __future__ import annotations
import hashlib
import hmac
import re
import time

SIG_RE = re.compile(r"^t=(\d+),v1=([0-9a-f]{64})$")
REPLAY_WINDOW_S = 300  # 5 minutes


class SignatureError(Exception):
    pass


def verify_signature(secret: str, header: str, raw_body: bytes,
                     now: float | None = None) -> None:
    m = SIG_RE.match(header.strip())
    if not m:
        raise SignatureError("malformed X-AgriCloud-Signature header")
    ts = int(m.group(1))
    sig = m.group(2)
    if abs((now or time.time()) - ts) > REPLAY_WINDOW_S:
        raise SignatureError(f"timestamp outside {REPLAY_WINDOW_S}s window")
    expected = hmac.new(
        secret.encode("utf-8"),
        f"{ts}.".encode("utf-8") + raw_body,
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, sig):
        raise SignatureError("HMAC mismatch")


if __name__ == "__main__":
    # Self-test
    secret = "whsec_demo_do_not_use_in_prod"
    raw = b'{"event_id":"a","event_type":"system.healthcheck","created_at":"2026-05-29T14:30:00Z"}'
    ts = int(time.time())
    digest = hmac.new(secret.encode(), f"{ts}.".encode() + raw, hashlib.sha256).hexdigest()
    header = f"t={ts},v1={digest}"
    verify_signature(secret, header, raw)
    print("OK: self-test verified", header[:25] + "...")
