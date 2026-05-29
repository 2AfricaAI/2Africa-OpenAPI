"""
SPDX-License-Identifier: Apache-2.0

2Africa OpenAPI - Privacy Manifest canonical hash (single file).

Vendor by:
    curl -O https://raw.githubusercontent.com/2AfricaAI/2Africa-OpenAPI/main/examples/helpers/python/manifest_hash.py

Computes the canonical SHA-256 hash of a parsed Privacy Manifest document
(spec chapter 4 §4.3). The canonicalisation rule is:

  1. Parse the YAML into the JSON Schema's data model.
  2. Re-serialise as JSON with object keys sorted lexicographically.
  3. Encode as UTF-8.
  4. sha256 -> hex digest prefixed with "sha256:".

Two implementations are provided so the file is dependency-free:
- ``hash_manifest_dict(d)``  - accepts a parsed dict / list / scalar.
- ``hash_manifest_yaml(s)``  - parses YAML text; needs PyYAML if you call it.

The header you send is ``X-Privacy-Manifest-Hash: <returned string>``.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


def _canonical_json(d: Any) -> bytes:
    """RFC 8785-aligned canonical JSON (sorted keys, no whitespace)."""
    return json.dumps(
        d,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def hash_manifest_dict(d: dict) -> str:
    """SHA-256 of the canonical JSON of a parsed Manifest dict."""
    digest = hashlib.sha256(_canonical_json(d)).hexdigest()
    return f"sha256:{digest}"


def hash_manifest_yaml(yaml_text: str) -> str:
    """Convenience wrapper for raw YAML text. Requires PyYAML."""
    try:
        import yaml  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            "hash_manifest_yaml requires PyYAML. "
            "Install with `pip install pyyaml`, "
            "or parse the YAML yourself and call hash_manifest_dict()."
        ) from e
    return hash_manifest_dict(yaml.safe_load(yaml_text))


if __name__ == "__main__":
    sample = {
        "manifest_version": "1.0.0",
        "profile": "balanced",
        "generated_at": "2026-05-29T14:30:00Z",
        "owner_id": "jane.doe@example-farm.ke",
        "endpoints": {
            "yields": {"enabled": True, "retention_days": 365},
        },
    }
    print(hash_manifest_dict(sample))
