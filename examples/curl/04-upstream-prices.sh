#!/usr/bin/env bash
# Submit a 1-record price batch.
set -euo pipefail
HOST="${OPENAPI_HOST:-https://sandbox.agricloud.2africa.ai}"
TOKEN="${OPENAPI_TOKEN:?set OPENAPI_TOKEN with scope upstream:prices}"
HASH="${MANIFEST_HASH:?set MANIFEST_HASH}"
curl -sS -i -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Spec-Version: 1.0.0-rc1" \
  -H "X-Privacy-Manifest-Hash: $HASH" \
  -H "Idempotency-Key: $(uuidgen)" \
  --data @- \
  "$HOST/v1/upstream/prices" << 'JSON'
{
  "tenant_pseudo_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "records": [{
    "record_id": "11111111-1111-1111-1111-111111111111",
    "sku_code": "TOMATO_GRADE_A",
    "region_code": "KE-30",
    "sold_on": "2026-05-22",
    "unit_price": { "amount": "75.00", "currency": "KES" },
    "per_unit": "kg"
  }]
}
JSON
