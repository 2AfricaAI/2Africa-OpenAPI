<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# 3 · Data Conventions

The conventions below apply to every endpoint and to all payloads
above the transport layer.

## 3.1 Naming

| Surface           | Style                | Examples                              |
| ----------------- | -------------------- | ------------------------------------- |
| JSON field names  | `snake_case`         | `crop_code`, `harvest_date`           |
| URL path segments | `kebab-case`         | `/v1/upstream/credit-pack`            |
| Constants / enums | `SCREAMING_SNAKE`    | `TOMATO`, `GLOBALG_A_P`, `BANK_KCB`   |
| Query params      | `snake_case`         | `region_code`, `page_size`            |
| HTTP headers      | `X-Kebab-Case`       | `X-Privacy-Manifest-Hash`             |

These rules are enforced by Spectral in `spec/.spectral.yml`. PRs
violating them fail CI.

## 3.2 Time

- Wire format MUST be **ISO 8601** with timezone designator `Z`
  (UTC). Example: `2026-05-29T14:30:00Z`.
- Date-only fields MUST be ISO 8601 calendar dates. Example:
  `2026-05-29`.
- Relative time (`P1D`, `now-7d`), local time without offset, and
  three-letter timezone abbreviations (`EAT`, `PST`) are forbidden.

## 3.3 Money

Money is **always** an object containing `amount` and `currency`.
Bare numbers are forbidden.

```json
{ "amount": "1234.50", "currency": "KES" }
```

- `amount` is a **string** (avoid float drift). Pattern
  `^-?\d+(\.\d{1,2})?$`. Servers MUST parse with a decimal
  (`BigDecimal`/`Decimal`) type, not a float.
- `currency` is ISO 4217 alpha-3. Currencies a tenant doesn't use
  MUST NOT be silently substituted.
- Maximum precision is 2 decimals across all v1.x endpoints. (A
  future RFC may relax this for fuel-and-feed payloads.)

## 3.4 Quantity

Physical quantities are similarly objects:

```json
{ "quantity": 1234.5, "unit": "kg" }
```

Allowed `unit` enum (v1.0): `kg`, `ton`, `crate`, `bag_25kg`,
`bag_50kg`, `litre`, `dozen`, `head`.

New units are added by MINOR release after RFC.

## 3.5 Identifiers

| Field                      | Format                                     |
| -------------------------- | ------------------------------------------ |
| `record_id`, `order_id`, … | UUID v4                                    |
| `tenant_pseudo_id`         | UUID v4 (stable pseudonym, not derivable)  |
| `crop_code`, `sku_code`    | `^[A-Z][A-Z0-9_]{1,31}$`                   |
| `recipient_id`             | `^[A-Z0-9_]{3,64}$`                        |

Business names (farm name, customer name, person name) are **never**
sent on the wire. The Privacy Manifest (chapter 4) enforces this at
schema level.

## 3.6 Region codes

```
<ISO 3166-1 alpha-2>-<ISO 3166-2 subdivision>
```

Examples:

| Code     | Meaning                              |
| -------- | ------------------------------------ |
| `KE-30`  | Nairobi County, Kenya                |
| `TZ-02`  | Arusha, Tanzania                     |
| `SN-DK`  | Dakar, Senegal                       |

Upstream data MUST NOT carry a region code more specific than the
second ISO 3166 level. A future MINOR release may add a separate
`ward_code` field gated by `region_floor: ward` in the manifest, but
**v1.0 forbids it**.

## 3.7 Cursor-based pagination

All list endpoints use opaque cursors.

Request:

```http
GET /v1/downstream/prices?region_code=KE-30&page_size=50&page_token=eyJv... HTTP/1.1
```

Response:

```json
{
  "items": [ /* … */ ],
  "next_page_token": "eyJ2…"
}
```

Rules:

- `page_size` is a hint, not a guarantee. Servers MAY return fewer
  items (e.g. to enforce the 30-row floor — see §3.10).
- `next_page_token` is **opaque** to the client. Clients MUST NOT
  decode, inspect, or modify it.
- Absence of `next_page_token` means "this was the last page".
- A token expires after **24 hours**. Stale tokens return
  `400 invalid_request`.

`offset` and `limit` parameters are forbidden on any endpoint.

## 3.8 Idempotency

Every mutating request (POST, PUT) MUST include an `Idempotency-Key`
header:

```http
Idempotency-Key: 3f55cd84-3a3a-46f3-9b1a-9e16f8b86e2a
```

- The value MUST be a UUID v4.
- Servers MUST dedupe over a window of **at least 24 hours**.
- A retry that arrives during the dedupe window MUST receive the
  original response plus the header `Idempotency-Replay: true`.
- A retry with the same key but a different body MUST be rejected
  with `409 idempotency_conflict` and the *first* request's outcome
  MUST be preserved.

## 3.9 Mandatory request headers

Every authenticated request MUST carry:

| Header                       | Why                                      |
| ---------------------------- | ---------------------------------------- |
| `Authorization: Bearer <jwt>` | Authn (chapter 2).                       |
| `X-Spec-Version`             | Version negotiation (chapter 1).         |

Every upstream request additionally MUST carry:

| Header                       | Why                                      |
| ---------------------------- | ---------------------------------------- |
| `X-Privacy-Manifest-Hash`    | Manifest binding (chapter 4).            |
| `Idempotency-Key`            | Replay safety (§3.8).                    |

## 3.10 The sample-size floor (privacy)

Servers MUST NOT return any aggregated row whose underlying sample
size is below **30**. This applies in particular to:

- `/v1/downstream/prices` rows (per region/sku/window).
- `/v1/downstream/benchmarks` snapshots.

When a row would have `sample_size < 30`, the server omits it from
the response and includes the next eligible row, possibly returning
fewer items than `page_size` requests. This is intentional and is
not an error.

## 3.11 Content negotiation

- `Content-Type` MUST be present on every request with a body.
- `application/json` is the default and only supported content type
  for v1.0 endpoints **except** `PUT /v1/privacy-manifest`, which
  takes `application/yaml`.
- Error responses use `application/problem+json` (RFC 7807; see
  chapter 8).
- `Accept` headers are honoured; clients that send
  `Accept: application/json` exclusively will still receive
  `application/problem+json` for errors — both are JSON.
