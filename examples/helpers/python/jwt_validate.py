"""
SPDX-License-Identifier: Apache-2.0

2Africa OpenAPI - Lightweight JWT claims validator (single file).

Vendor by:
    curl -O https://raw.githubusercontent.com/2AfricaAI/2Africa-OpenAPI/main/examples/helpers/python/jwt_validate.py

This file intentionally does NOT verify the signature itself - we trust
established libraries for that and only encode the project-specific claim
rules (iss / aud / scope / exp leeway) here.

Recommended pairing:
    pip install pyjwt[crypto] cryptography

    import jwt
    from jwt_validate import validate_claims, require_scope

    # Verify signature using the JWKS published at /.well-known/jwks.json
    payload = jwt.decode(token, key, algorithms=["RS256"], audience="openapi.2africa.ai")
    validate_claims(payload, expected_iss="https://api.agricloud.2africa.ai")
    require_scope(payload, "upstream:yields")
"""
from __future__ import annotations

import time
from typing import Mapping


class ClaimError(Exception):
    """Raised when JWT claims do not meet 2Africa OpenAPI rules."""


def validate_claims(
    payload: Mapping[str, object],
    *,
    expected_iss: str,
    expected_aud: str = "openapi.2africa.ai",
    leeway_s: int = 30,
    now: float | None = None,
) -> None:
    """Check iss / aud / exp / iat / not_before claims per spec chapter 2."""
    iss = payload.get("iss")
    if iss != expected_iss:
        raise ClaimError(f"unexpected iss: {iss!r}")
    aud = payload.get("aud")
    audiences = [aud] if isinstance(aud, str) else (list(aud) if aud else [])
    if expected_aud not in audiences:
        raise ClaimError(f"aud does not include {expected_aud!r}: got {audiences!r}")
    current = now if now is not None else time.time()
    exp = payload.get("exp")
    if exp is None or current > float(exp) + leeway_s:
        raise ClaimError("token expired")
    iat = payload.get("iat")
    if iat is not None and float(iat) - leeway_s > current:
        raise ClaimError("token iat is in the future")
    nbf = payload.get("nbf")
    if nbf is not None and float(nbf) - leeway_s > current:
        raise ClaimError("token not yet valid (nbf)")


def require_scope(payload: Mapping[str, object], scope: str) -> None:
    """Raise ClaimError if `scope` is not in the token's `scope` claim."""
    s = payload.get("scope", "")
    if not isinstance(s, str):
        raise ClaimError("scope claim is not a string")
    if scope not in s.split():
        raise ClaimError(f"missing required scope: {scope}")


if __name__ == "__main__":
    sample = {
        "iss": "https://api.agricloud.2africa.ai",
        "aud": "openapi.2africa.ai",
        "iat": int(time.time()) - 60,
        "exp": int(time.time()) + 3500,
        "scope": "upstream:yields privacy:manage",
    }
    validate_claims(sample, expected_iss="https://api.agricloud.2africa.ai")
    require_scope(sample, "upstream:yields")
    print("OK: sample token passed all claim checks")
