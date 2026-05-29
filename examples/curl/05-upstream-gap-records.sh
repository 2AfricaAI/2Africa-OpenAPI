#!/usr/bin/env bash
# Submit a GAP audit record.
set -euo pipefail
HOST="${OPENAPI_HOST:-https://sandbox.agricloud.2africa.ai}"
TOKEN="${OPENAPI_TOKEN:?set OPENAPI_TOKEN with scope upstream:gap}"
HASH="${MANIFEST_HASH:?set MANIFEST_HASH}"
curl -sS -i -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Spec-Version: 1.0.0-rc1" \
  -H "X-Privacy-Manifest-Hash: $HASH" \
  -H "Idempotency-Key: $(uuidgen)" \
  --data @- \
  "$HOST/v1/upstream/gap-records" << 'JSON'
{
  "tenant_pseudo_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "records": [{
    "record_id": "22222222-2222-2222-2222-222222222222",
    "audit_date": "2026-04-12",
    "scheme": "GLOBALG_A_P",
    "result": "pass",
    "non_conformities": 0,
    "region_code": "KE-30"
  }]
}
JSON
