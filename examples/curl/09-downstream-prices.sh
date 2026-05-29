#!/usr/bin/env bash
# Regional median price for tomato grade A in Nairobi county, last 30 days.
set -euo pipefail
HOST="${OPENAPI_HOST:-https://sandbox.agricloud.2africa.ai}"
TOKEN="${OPENAPI_TOKEN:?set OPENAPI_TOKEN with scope downstream:prices}"
curl -sS -i \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Spec-Version: 1.0.0-rc1" \
  "$HOST/v1/downstream/prices?region_code=KE-30&sku_code=TOMATO_GRADE_A&window=30d"
