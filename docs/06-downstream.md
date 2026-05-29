<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# 6 · Downstream Endpoints

All five downstream endpoints are GET, cursor-paginated, and ON by
default for any client whose token carries the appropriate scope.
There is no Privacy Manifest on downstream — it controls only what
travels *upstream*.

| Path                              | Scope                       | Required params       |
| --------------------------------- | --------------------------- | --------------------- |
| `/v1/downstream/dictionaries`     | `downstream:dictionaries`   | `kind?`               |
| `/v1/downstream/prices`           | `downstream:prices`         | `region_code`         |
| `/v1/downstream/benchmarks`       | `downstream:benchmarks`     | `region_code`, `crop_code` |
| `/v1/downstream/marketplace`      | `downstream:marketplace`    | `region_code`         |
| `/v1/downstream/procurement`      | `downstream:procurement`    | `region_code`         |

Mandatory headers:

```http
Authorization: Bearer <jwt>
X-Spec-Version: 1.0.0-rc1
```

For full schemas see [`spec/openapi.yaml`](../spec/openapi.yaml).

## 6.1 Pagination

All five endpoints use the cursor pattern in chapter 3 §3.7:

```http
GET /v1/downstream/prices?region_code=KE-30&page_size=50&page_token=<opaque>
```

```json
{
  "items": [ /* ... */ ],
  "next_page_token": "<opaque>"
}
```

Servers MAY return fewer items than `page_size` when applying the
sample-size floor (§3.10).

## 6.2 GET /v1/downstream/dictionaries

Returns the platform's authoritative reference data.

Query:

| Param | Required | Notes                                                    |
| ----- | -------- | -------------------------------------------------------- |
| `kind` | no      | One of `crop`, `sku`, `region`, `unit`, `currency`. If absent, returns all kinds interleaved (`kind` is in each row). |

Row schema:

```json
{
  "code":  "TOMATO",
  "kind":  "crop",
  "label": "Tomato (Solanum lycopersicum)",
  "synonyms": ["Nyanya", "Tomati"]
}
```

Cache hint: responses SHOULD carry `Cache-Control: max-age=3600`.
Clients invalidate on the `dictionary.updated` webhook (Sprint 2,
not in v1.0).

## 6.3 GET /v1/downstream/prices

Median / p25 / p75 prices per SKU per region per rolling window.

Query:

| Param        | Required | Notes                                          |
| ------------ | -------- | ---------------------------------------------- |
| `region_code` | yes     | ISO 3166-1/2 (chapter 3 §3.6).                 |
| `sku_code`   | no       | Restrict to one SKU.                           |
| `window`     | no       | `7d` / `30d` / `90d`. Default `30d`.           |

Row schema:

```json
{
  "sku_code":    "TOMATO_GRADE_A",
  "region_code": "KE-30",
  "window":      "30d",
  "p25":         { "amount": "68.00", "currency": "KES" },
  "median":      { "amount": "75.00", "currency": "KES" },
  "p75":         { "amount": "82.00", "currency": "KES" },
  "sample_size": 142
}
```

Rows with `sample_size < 30` MUST NOT appear in the response (§3.10).

Typical UI use: an AgriOS dashboard card *"Your price KES 75 / kg vs
regional median KES 82 / kg in last 30 days."*

## 6.4 GET /v1/downstream/benchmarks

Peer benchmarks for a (region, crop, size_band) tuple.

Query:

| Param        | Required | Notes                                              |
| ------------ | -------- | -------------------------------------------------- |
| `region_code` | yes     | ISO 3166-1/2.                                      |
| `crop_code`  | yes      | `^[A-Z][A-Z0-9_]{1,31}$`.                          |
| `size_band`  | no       | `smallholder` / `medium` / `large`.                |

Response shape (single object, not a page):

```json
{
  "region_code": "KE-30",
  "crop_code":   "TOMATO",
  "size_band":   "smallholder",
  "window":      "90d",
  "metrics": {
    "yield_per_hectare_kg": 18500,
    "cost_per_kg":          { "amount": "32.40", "currency": "KES" },
    "gross_margin_pct":     54.6,
    "sample_size":          78
  }
}
```

`sample_size < 30` returns `404 not_found`. (A 200 with a null
metrics object would mislead UIs.)

## 6.5 GET /v1/downstream/marketplace

Open sourcing orders matching the client's region.

Row schema:

```json
{
  "order_id":     "<UUID v4>",
  "sku_code":     "TOMATO_GRADE_A",
  "region_code":  "KE-30",
  "quantity":     { "quantity": 5000, "unit": "kg" },
  "target_price": { "amount": "78.00", "currency": "KES" },
  "buyer_kind":   "retailer",
  "posted_at":    "2026-05-29T09:00:00Z",
  "expires_at":   "2026-06-05T17:00:00Z"
}
```

Buyer identity (real name, contact info) is NOT in the wire schema.
A response endpoint for the seller to commit to an order is
out-of-scope for v1.0; it is planned in RFC-021 for v1.1.

## 6.6 GET /v1/downstream/procurement

Group-buy opportunities (collective procurement).

Query:

| Param        | Required | Notes                                                  |
| ------------ | -------- | ------------------------------------------------------ |
| `region_code` | yes     | ISO 3166-1/2.                                          |
| `category`   | no       | `seed` / `fertiliser` / `pesticide` / `equipment` / `packaging` / `other`. |

Row schema:

```json
{
  "opportunity_id": "<UUID v4>",
  "category":       "fertiliser",
  "sku_code":       "DAP_50KG",
  "region_code":    "KE-30",
  "unit_price_at_threshold": { "amount": "2950.00", "currency": "KES" },
  "threshold": { "committed": 240, "required": 500 },
  "posted_at":   "2026-05-29T09:00:00Z",
  "expires_at":  "2026-06-05T17:00:00Z"
}
```

The buyer commits via the platform UI; v1.0 does not include a
commit endpoint in the spec.

### 6.5.1 POST /v1/downstream/marketplace/{order_id}/responses (v1.1)

Added in v1.1 (RFC-021). Lets a seller submit an in-protocol response
to a marketplace order so the audit trail and the Privacy Manifest
allow-list both cover what used to happen out-of-band.

Required scope: `marketplace:respond` (not implied by
`downstream:marketplace`).

Body:

```json
{
  "seller_pseudo_id":   "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "offered_quantity":   { "quantity": 5000, "unit": "kg" },
  "offered_unit_price": { "amount": "78.50", "currency": "KES" },
  "available_from":     "2026-06-01",
  "available_until":    "2026-06-10",
  "notes":              "Free delivery within KE-30 for orders >= 1 t."
}
```

Response 201:

```json
{
  "response_id":    "<UUID v4>",
  "order_id":       "<UUID v4>",
  "accepted_at":    "2026-05-29T14:30:00Z",
  "buyer_notified": true
}
```

Servers MUST reject:

- `404 Not Found` if `order_id` does not exist.
- `410 Gone` if the order has expired.
- `409 Conflict` if the same `seller_pseudo_id` already responded to
  this `order_id`.

After acceptance, the server delivers `marketplace.response_received`
to the buyer (new webhook event added in v1.1).

## 6.7 Caching guidance

| Endpoint        | Typical `max-age` | Invalidate on webhook                |
| --------------- | ----------------- | ------------------------------------ |
| dictionaries    | 1 h               | dictionary.updated (post-v1.0)       |
| prices          | 5 min             | `pricing.price_updated`              |
| benchmarks      | 1 h               | `pricing.benchmark_refreshed`        |
| marketplace     | 1 min             | `marketplace.order_posted`           |
| procurement     | 5 min             | `procurement.opportunity_opened`     |

Clients SHOULD honour `Cache-Control` headers literally and reduce
load on the platform proportionally.
