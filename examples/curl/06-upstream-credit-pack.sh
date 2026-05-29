#!/usr/bin/env bash
# One-shot credit pack delivered to a pre-approved bank.
set -euo pipefail
HOST="${OPENAPI_HOST:-https://sandbox.agricloud.2africa.ai}"
TOKEN="${OPENAPI_TOKEN:?set OPENAPI_TOKEN with scope upstream:credit-pack}"
HASH="${MANIFEST_HASH:?set MANIFEST_HASH}"
curl -sS -i -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Spec-Version: 1.0.0-rc1" \
  -H "X-Privacy-Manifest-Hash: $HASH" \
  -H "Idempotency-Key: $(uuidgen)" \
  --data @- \
  "$HOST/v1/upstream/credit-pack" << 'JSON'
{
  "pack_id": "33333333-3333-3333-3333-333333333333",
  "tenant_pseudo_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "recipient_id": "BANK_KCB",
  "period_start": "2025-05-01",
  "period_end":   "2026-04-30",
  "financials": {
    "revenue":           { "amount": "4800000.00", "currency": "KES" },
    "cost_of_goods":     { "amount": "3100000.00", "currency": "KES" },
    "gross_profit":      { "amount": "1700000.00", "currency": "KES" },
    "open_orders_value": { "amount":  "850000.00", "currency": "KES" }
  },
  "assets": [
    { "kind": "land",      "valuation": { "amount": "12000000.00", "currency": "KES" }, "description": "8 ha freehold" },
    { "kind": "equipment", "valuation": {  "amount":   "950000.00", "currency": "KES" }, "description": "Drip irrigation + 2 tractors" }
  ]
}
JSON
