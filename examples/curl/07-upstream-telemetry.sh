#!/usr/bin/env bash
# Anonymous client-health telemetry.
set -euo pipefail
HOST="${OPENAPI_HOST:-https://sandbox.agricloud.2africa.ai}"
TOKEN="${OPENAPI_TOKEN:?set OPENAPI_TOKEN with scope upstream:telemetry}"
HASH="${MANIFEST_HASH:?set MANIFEST_HASH}"
curl -sS -i -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Spec-Version: 1.0.0-rc1" \
  -H "X-Privacy-Manifest-Hash: $HASH" \
  --data @- \
  "$HOST/v1/upstream/telemetry" << 'JSON'
{
  "tenant_pseudo_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "events": [
    { "event": "dashboard.opened",    "occurred_at": "2026-05-29T08:12:03Z", "sdk_version": "0.1.0", "os": "linux" },
    { "event": "harvest.entered",     "occurred_at": "2026-05-29T08:14:50Z", "sdk_version": "0.1.0", "os": "linux" }
  ]
}
JSON
