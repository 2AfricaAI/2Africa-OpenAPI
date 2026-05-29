#!/usr/bin/env bash
# Publish the active Privacy Manifest. Run this before any upstream call.
set -euo pipefail
HOST="${OPENAPI_HOST:-https://sandbox.agricloud.2africa.ai}"
TOKEN="${OPENAPI_TOKEN:?set OPENAPI_TOKEN to a JWT with scope privacy:manage}"
MANIFEST="${1:-./manifests/balanced.yaml}"
curl -sS -i -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/yaml" \
  -H "X-Spec-Version: 1.0.0-rc1" \
  -H "Idempotency-Key: $(uuidgen)" \
  --data-binary "@$MANIFEST" \
  "$HOST/v1/privacy-manifest"
