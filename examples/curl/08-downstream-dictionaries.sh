#!/usr/bin/env bash
# Pull standard crops dictionary.
set -euo pipefail
HOST="${OPENAPI_HOST:-https://sandbox.agricloud.2africa.ai}"
TOKEN="${OPENAPI_TOKEN:?set OPENAPI_TOKEN with scope downstream:dictionaries}"
curl -sS -i \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Spec-Version: 1.0.0-rc1" \
  "$HOST/v1/downstream/dictionaries?kind=crop&page_size=50"
