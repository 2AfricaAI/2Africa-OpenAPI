#!/usr/bin/env bash
# Open group-buy opportunities for fertiliser in KE-30.
set -euo pipefail
HOST="${OPENAPI_HOST:-https://sandbox.agricloud.2africa.ai}"
TOKEN="${OPENAPI_TOKEN:?set OPENAPI_TOKEN with scope downstream:procurement}"
curl -sS -i \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Spec-Version: 1.0.0-rc1" \
  "$HOST/v1/downstream/procurement?region_code=KE-30&category=fertiliser"
