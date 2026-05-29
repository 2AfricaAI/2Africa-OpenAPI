"""
SPDX-License-Identifier: Apache-2.0

2Africa OpenAPI - PKCE helper (single file, no deps beyond stdlib).

Vendor by:
    curl -O https://raw.githubusercontent.com/2AfricaAI/2Africa-OpenAPI/main/examples/helpers/python/pkce.py

Usage during the OAuth Authorization Code + PKCE flow (spec chapter 2):

    from pkce import generate_pkce_pair

    verifier, challenge = generate_pkce_pair()
    # Send `challenge` (+ `code_challenge_method=S256`) on /oauth/authorize.
    # Keep `verifier` server-side and send it on /oauth/token.
"""
from __future__ import annotations

import base64
import hashlib
import secrets

# RFC 7636 says verifier is 43..128 chars from the URL-safe alphabet.
# 32 random bytes -> 43 base64url chars -> well within bounds.
_DEFAULT_VERIFIER_BYTES = 32


def generate_code_verifier(num_bytes: int = _DEFAULT_VERIFIER_BYTES) -> str:
    """Generate a cryptographically random PKCE code_verifier."""
    if not 32 <= num_bytes <= 96:
        raise ValueError("num_bytes must be 32..96 to keep verifier in 43..128 chars")
    raw = secrets.token_bytes(num_bytes)
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def code_challenge_s256(verifier: str) -> str:
    """Compute the PKCE S256 code_challenge from a verifier."""
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def generate_pkce_pair(num_bytes: int = _DEFAULT_VERIFIER_BYTES) -> tuple[str, str]:
    """Return ``(verifier, challenge)``."""
    verifier = generate_code_verifier(num_bytes)
    return verifier, code_challenge_s256(verifier)


if __name__ == "__main__":
    v, c = generate_pkce_pair()
    print(f"code_verifier  = {v}")
    print(f"code_challenge = {c}")
    print(f"  (len verifier={len(v)}, challenge={len(c)})")
