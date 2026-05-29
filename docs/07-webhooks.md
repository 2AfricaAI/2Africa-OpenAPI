<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# 7 · Webhooks

The platform pushes events to subscribed clients. The full machine-
readable contract is
[`spec/webhooks.asyncapi.yaml`](../spec/webhooks.asyncapi.yaml).

## 7.1 Subscription

Subscribed during client registration (out-of-band; see chapter 2
§2.2). The platform issues a **webhook secret** at the same time as
the client_secret:

```json
{
  "webhook_secret":   "whsec_8sd...",
  "delivery_url":     "https://farm.example.ke/webhooks/agricloud",
  "subscribed_events": [
    "pricing.price_updated",
    "marketplace.order_posted"
  ]
}
```

The client is free to subscribe to any subset of available event
types. A subscription change is a separate out-of-band operation.

## 7.2 Event types in v1.0

| Channel                          | Event type                       |
| -------------------------------- | -------------------------------- |
| `system.healthcheck`             | `system.healthcheck`             |
| `pricing.price-updated`          | `pricing.price_updated`          |
| `pricing.benchmark-refreshed`    | `pricing.benchmark_refreshed`    |
| `marketplace.order-posted`       | `marketplace.order_posted`       |
| `procurement.opportunity-opened` | `procurement.opportunity_opened` |
| `telemetry.config-changed`       | `telemetry.config_changed`       |

URL slug is kebab-case; the `event_type` value in the payload is
dot-separated snake_case (matches the channel path scheme used in
internal logging).

## 7.3 Delivery shape

```http
POST /webhooks/agricloud HTTP/1.1
Host: farm.example.ke
Content-Type: application/json
X-AgriCloud-Signature: t=1748520123,v1=8a4c6e1...
X-AgriCloud-Spec-Version: 1.0.0-rc1
X-AgriCloud-Delivery-Id: 1f2d3e4c-...
X-AgriCloud-Event-Type: pricing.price_updated

{
  "event_id":    "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "event_type":  "pricing.price_updated",
  "created_at":  "2026-05-29T14:30:00Z",
  "region_code": "KE-30",
  "sku_code":    "TOMATO_GRADE_A",
  "window":      "30d",
  "sample_size": 142
}
```

Pricing events deliberately do **not** carry the new figures — only
the (region, sku, window) tuple. Receivers re-fetch via
`GET /v1/downstream/prices` if they care. This keeps webhook payloads
small (cheap on mobile data) and limits replay-attack damage.

## 7.4 Signature verification

The signature header:

```
X-AgriCloud-Signature: t=<unix>,v1=<hex_hmac_sha256>
```

The HMAC is computed over the byte sequence `f"{t}.{raw_body}"`
using the **webhook secret** as key. SHA-256 hash. Hex-encoded
lower-case.

### 7.4.1 Verification algorithm (receiver side)

1. Parse `t` and `v1` from the header.
2. Reject if `abs(now - t) > 300` (5-minute replay window).
3. Compute `expected = hex(HMAC-SHA256(secret, f"{t}.{raw_body}"))`.
4. Compare `expected` with `v1` using **constant-time** comparison.
5. If equal, accept; otherwise reject the delivery.

A reference Python implementation is in
[`examples/webhook-replay/verify_signature.py`](../examples/webhook-replay/verify_signature.py).

### 7.4.2 Why the body, not the headers?

The HMAC binds to the request body, not to the headers. A
man-in-the-middle who alters the body would invalidate the
signature. Header tampering (e.g. inserting a fake
`X-AgriCloud-Spec-Version`) is detectable independently by the
receiver's own logging.

## 7.5 Idempotency

`event_id` is unique per event. Receivers MUST dedupe on it: if an
`event_id` has been processed in the last 24 hours, the receiver
returns 2xx without re-processing.

`X-AgriCloud-Delivery-Id` differs per delivery attempt; useful to
correlate with platform-side logs but NOT a dedupe key.

## 7.6 Retry schedule

Failed deliveries (non-2xx response, timeout > 30 s, connection
error) are retried with exponential backoff:

```
1 min → 5 min → 30 min → 2 h → 6 h
```

Five attempts total over up to 24 hours. After the fifth failure,
the platform stops retrying and emits a `webhook.delivery_failed`
internal alert (out of scope for v1.0 spec).

Receivers SHOULD respond with 2xx as quickly as possible and process
asynchronously. The 30-second response budget is firm; longer
processing belongs in a background job.

## 7.7 Catching up after downtime

If a receiver is offline for an extended period, the platform's
retry budget will eventually exhaust. To catch up:

- v1.0 has no backfill endpoint. Receivers MUST re-fetch the
  affected downstream resource (`/v1/downstream/prices` etc.) when
  they come back online.
- A backfill endpoint `GET /v1/events?since=<timestamp>` is planned
  for v1.1 (RFC-019).

## 7.8 Health-check event

`system.healthcheck` carries no business content. It exists so:

1. The compliance test suite (CTS) can validate a receiver's
   signature implementation end-to-end.
2. The platform can verify a `delivery_url` reachability during
   onboarding.

Payload:

```json
{
  "event_id":   "<UUID v4>",
  "event_type": "system.healthcheck",
  "created_at": "2026-05-29T14:30:00Z"
}
```

Receivers MUST respond 2xx and dedupe by `event_id` like any other
event.
