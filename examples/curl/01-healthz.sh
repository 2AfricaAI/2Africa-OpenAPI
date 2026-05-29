#!/usr/bin/env bash
# Public liveness probe. No token needed.
set -euo pipefail
HOST="${OPENAPI_HOST:-https://sandbox.agricloud.2africa.ai}"
curl -sS -i \
  -H "X-Spec-Version: 1.0.0-rc1" \
  "$HOST/healthz" | sed 's/^/  /'
