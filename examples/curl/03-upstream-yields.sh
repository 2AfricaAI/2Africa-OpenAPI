#!/usr/bin/env bash
# Submit a 2-record yield batch.
set -euo pipefail
HOST="${OPENAPI_HOST:-https://sandbox.agricloud.2africa.ai}"
TOKEN="${OPENAPI_TOKEN:?set OPENAPI_TOKEN with scope upstream:yields}"
HASH="${MANIFEST_HASH:?set MANIFEST_HASH to the sha256 of your active manifest}"
curl -sS -i -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Spec-Version: 1.0.0-rc1" \
  -H "X-Privacy-Manifest-Hash: $HASH" \
  -H "Idempotency-Key: $(uuidgen)" \
  --data @- \
  "$HOST/v1/upstream/yields" << 'JSON'
{
  "tenant_pseudo_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "records": [
    {
      "record_id": "8d6c4c3a-1234-4abc-9def-aaaabbbbcccc",
      "crop_code": "TOMATO",
      "region_code": "KE-30",
      "harvest_date": "2026-05-20",
      "quantity": { "quantity": 1234.5, "unit": "kg" }
    },
    {
      "record_id": "8d6c4c3a-1234-4abc-9def-aaaabbbbdddd",
      "crop_code": "MAIZE",
      "region_code": "KE-30",
      "harvest_date": "2026-05-21",
      "quantity": { "quantity": 9800, "unit": "kg" }
    }
  ]
}
JSON
