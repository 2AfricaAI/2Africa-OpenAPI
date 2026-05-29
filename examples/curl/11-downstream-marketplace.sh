#!/usr/bin/env bash
# Open buyer orders in KE-30.
set -euo pipefail
HOST="${OPENAPI_HOST:-https://sandbox.agricloud.2africa.ai}"
TOKEN="${OPENAPI_TOKEN:?set OPENAPI_TOKEN with scope downstream:marketplace}"
curl -sS -i \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Spec-Version: 1.0.0-rc1" \
  "$HOST/v1/downstream/marketplace?region_code=KE-30&page_size=20"
