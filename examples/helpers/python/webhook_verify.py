"""
SPDX-License-Identifier: Apache-2.0

2Africa OpenAPI - HMAC-SHA256 webhook verifier (single file).

Vendor by:
    curl -O https://raw.githubusercontent.com/2AfricaAI/2Africa-OpenAPI/main/examples/helpers/python/webhook_verify.py

Usage in your HTTP handler (spec chapter 7 §7.4):

    raw = request.get_data()  # MUST be the raw bytes, BEFORE JSON parsing
    verify_signature(
        secret    = os.environ["WEBHOOK_SECRET"],
        header    = request.headers["X-AgriCloud-Signature"],
        raw_body  = raw,
    )

Raises SignatureError on any failure: malformed header, replay outside the
5-minute window, or HMAC mismatch. Otherwise returns None.
"""
from __future__ import annotations

import hashlib
import hmac
import re
import time

_SIG_RE = re.compile(r"^t=(\d+),v1=([0-9a-f]{64})$")
REPLAY_WINDOW_S = 300  # 5 minutes


class SignatureError(Exception):
    """Raised when a webhook delivery fails signature verification."""


def verify_signature(
    secret: str,
    header: str,
    raw_body: bytes,
    now: float | None = None,
) -> None:
    """Verify the X-AgriCloud-Signature header against the raw body."""
    m = _SIG_RE.match(header.strip())
    if not m:
        raise SignatureError("malformed X-AgriCloud-Signature header")
    ts = int(m.group(1))
    sig = m.group(2)
    current = now if now is not None else time.time()
    if abs(current - ts) > REPLAY_WINDOW_S:
        raise SignatureError(f"timestamp outside {REPLAY_WINDOW_S}s window")
    expected = hmac.new(
        secret.encode("utf-8"),
        f"{ts}.".encode("utf-8") + raw_body,
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, sig):
        raise SignatureError("HMAC mismatch")


if __name__ == "__main__":
    secret = "whsec_demo_do_not_use_in_prod"
    raw = b'{"event_id":"a","event_type":"system.healthcheck","created_at":"2026-05-29T14:30:00Z"}'
    ts = int(time.time())
    digest = hmac.new(secret.encode(), f"{ts}.".encode() + raw, hashlib.sha256).hexdigest()
    header = f"t={ts},v1={digest}"
    verify_signature(secret, header, raw)
    print("OK:", header[:25] + "...")
