<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# 5 · Upstream Endpoints

All five upstream endpoints are POST, require an active Privacy
Manifest (chapter 4), and are OFF by default. Each requires its own
OAuth scope.

| Path                            | Scope                  | Default body limit | Async? |
| ------------------------------- | ---------------------- | ------------------ | ------ |
| `/v1/upstream/yields`           | `upstream:yields`      | 1 000 records      | 202    |
| `/v1/upstream/prices`           | `upstream:prices`      | 1 000 records      | 202    |
| `/v1/upstream/gap-records`      | `upstream:gap`         |   500 records      | 202    |
| `/v1/upstream/credit-pack`      | `upstream:credit-pack` | 1 pack             | 201    |
| `/v1/upstream/telemetry`        | `upstream:telemetry`   | 10 000 events      | 204    |

For full schemas, see [`spec/openapi.yaml`](../spec/openapi.yaml).

## 5.1 Common request shape

Every batch endpoint takes:

```json
{
  "tenant_pseudo_id": "<UUID v4>",
  "records": [ /* 1..maxItems */ ]
}
```

Mandatory headers (chapter 3 §3.9):

```http
Authorization: Bearer <jwt>
X-Spec-Version: 1.0.0-rc1
X-Privacy-Manifest-Hash: sha256:...
Idempotency-Key: <UUID v4>
Content-Type: application/json
```

## 5.2 POST /v1/upstream/yields

Submit anonymous harvest yields.

### Record schema

```json
{
  "record_id":     "<UUID v4>",
  "crop_code":     "TOMATO",
  "region_code":   "KE-30",
  "harvest_date":  "2026-05-20",
  "quantity":      { "quantity": 1234.5, "unit": "kg" },
  "gap_compliant": true                                    // optional
}
```

### Response 202

```json
{
  "batch_id":       "<UUID v4>",
  "accepted_count": 2,
  "accepted_at":    "2026-05-29T14:30:00Z"
}
```

Servers MAY reject individual records out of a batch; the
`accepted_count` says how many were taken. Rejected records are
surfaced via a webhook event in a future MINOR (`upstream.record_rejected`).

## 5.3 POST /v1/upstream/prices

Submit anonymous sale prices.

### Record schema

```json
{
  "record_id":   "<UUID v4>",
  "sku_code":    "TOMATO_GRADE_A",
  "region_code": "KE-30",
  "sold_on":     "2026-05-22",
  "unit_price":  { "amount": "75.00", "currency": "KES" },
  "per_unit":    "kg"
}
```

Buyer identity, contract terms, and absolute volumes are excluded by
the spec schema — there is no field for them. A client that wants to
share those builds them in a separate, non-standard endpoint outside
this spec.

## 5.4 POST /v1/upstream/gap-records

Submit Good Agricultural Practice audit records.

```json
{
  "record_id":         "<UUID v4>",
  "audit_date":        "2026-04-12",
  "scheme":            "GLOBALG_A_P",
  "result":            "pass",
  "non_conformities":  0,
  "region_code":       "KE-30"
}
```

`scheme` enum: `GLOBALG_A_P`, `KENYA_GAP`, `ORGANIC_KE`, `FAIRTRADE`,
`RAINFOREST_ALLIANCE`, `OTHER`.

GAP records often feed certification-body reports; the same record
may also be the basis of a downstream marketplace listing. Cross-
endpoint correlation, however, happens entirely on the platform
side; the client just submits.

## 5.5 POST /v1/upstream/credit-pack

A **one-shot**, non-periodic endpoint. The owner triggers this when
applying for a loan; the body packages 12 months of P&L, open
orders, and asset valuation, and is delivered to a single bank
identified by `recipient_id`. Manifest's
`endpoints.credit_pack.recipients` MUST contain that `recipient_id`,
or the call fails `422 manifest_field_not_allowed`.

Each `pack_id` is single-use; reusing one returns
`409 idempotency_conflict`.

### Schema

```json
{
  "pack_id":          "<UUID v4>",
  "tenant_pseudo_id": "<UUID v4>",
  "recipient_id":     "BANK_KCB",
  "period_start":     "2025-05-01",
  "period_end":       "2026-04-30",
  "financials": {
    "revenue":           { "amount": "4800000.00", "currency": "KES" },
    "cost_of_goods":     { "amount": "3100000.00", "currency": "KES" },
    "gross_profit":      { "amount": "1700000.00", "currency": "KES" },
    "open_orders_value": { "amount":  "850000.00", "currency": "KES" }
  },
  "assets": [
    { "kind": "land",      "valuation": { "amount": "12000000.00", "currency": "KES" }, "description": "8 ha freehold" },
    { "kind": "equipment", "valuation": {  "amount":   "950000.00", "currency": "KES" }, "description": "Drip + 2 tractors" }
  ]
}
```

### Response 201

```json
{
  "pack_id":      "<UUID v4>",
  "accepted_at":  "2026-05-29T14:30:00Z",
  "delivered_to": "BANK_KCB"
}
```

The bank then accesses the pack inside the platform under whatever
UX the platform provides; the wire contract ends at "delivered".

## 5.6 POST /v1/upstream/telemetry

Anonymous client-health telemetry. The Manifest's
`endpoints.telemetry` controls which event names are permitted.
Servers SHOULD silently drop unknown event names rather than reject
the batch.

### Event schema

```json
{
  "event":       "dashboard.opened",
  "occurred_at": "2026-05-29T08:12:03Z",
  "sdk_version": "0.1.0",
  "os":          "linux"
}
```

`event` pattern: `^[a-z][a-z0-9_]{1,63}\.[a-z][a-z0-9_]{1,63}$` —
two snake_case segments joined by a dot. The first segment names a
subsystem; the second names a verb.

No `tenant_pseudo_id` correlation across telemetry batches is
permitted in v1.0. (A future RFC may relax this for active-user
counts.)

### Response 204

No body.

## 5.7 Batch-level error mapping

| Outcome                                                  | Status |
| -------------------------------------------------------- | ------ |
| Whole batch accepted                                     | 202 (or 201 / 204 per endpoint) |
| Request malformed (e.g. missing required header)         | 400    |
| Token missing / expired                                  | 401    |
| Token authentic but lacks scope                          | 403    |
| Re-used `Idempotency-Key` with a different body          | 409    |
| Manifest hash mismatch                                   | 422    |
| Field outside Manifest allow-list                        | 422    |
| Rate limit exhausted                                     | 429    |

The full error model is described in [chapter 8](./08-errors.md).
