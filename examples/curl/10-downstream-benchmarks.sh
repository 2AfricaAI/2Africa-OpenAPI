#!/usr/bin/env bash
# Peer benchmark: tomato smallholders in KE-30, 90-day window.
set -euo pipefail
HOST="${OPENAPI_HOST:-https://sandbox.agricloud.2africa.ai}"
TOKEN="${OPENAPI_TOKEN:?set OPENAPI_TOKEN with scope downstream:benchmarks}"
curl -sS -i \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Spec-Version: 1.0.0-rc1" \
  "$HOST/v1/downstream/benchmarks?region_code=KE-30&crop_code=TOMATO&size_band=smallholder"
