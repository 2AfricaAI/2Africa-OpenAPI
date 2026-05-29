<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# RFC-019: Webhook Backfill via `GET /v1/events`

| Field             | Value                                   |
| ----------------- | --------------------------------------- |
| Status            | Accepted                                |
| Author            | 2Africa OpenAPI Maintainers             |
| Created           | 2026-05-29                              |
| Comment window    | 14 days from Open                       |
| Target version    | v1.1                                    |
| First implementer | 2Africa AgriCloud v1.1                  |

## Problem

The current spec (v1.0.0-rc1) describes webhook delivery with 5 retries
across 24 hours (chapter 7 §7.5). If a receiver is offline for longer
than that window, events are lost. The spec text in
`spec/webhooks.asyncapi.yaml` already notes:

> "If the receiver missed events while offline, it MAY call
> `GET /v1/events?since=<timestamp>` to backfill (Sprint 2 endpoint;
> not in v1.0)."

— but the endpoint itself was deferred. Implementers reported this is
the single most common reason webhook deliveries silently disappear in
their test deployments.

## Proposal

Add a new downstream endpoint:

```
GET /v1/events?since=<unix_seconds>&page_size=N&page_token=...
```

Returns events the server would have delivered between `since` and
`now()`, in chronological order, with the same payload + headers shape
as the live webhook delivery (chapter 7 §7.3).

### Request

| Parameter   | Required | Notes                                                   |
| ----------- | -------- | ------------------------------------------------------- |
| `since`     | yes      | Unix timestamp (seconds). MUST be within the past 30 days. |
| `page_size` | no       | Default 50, max 200.                                    |
| `page_token`| no       | Cursor from previous page.                              |
| `event_type`| no       | Filter to one event type (e.g. `pricing.price_updated`). |

### Response

```json
{
  "items": [
    {
      "delivery_id":     "<UUID v4>",
      "signature":       "t=1748520123,v1=8a4c6e1...",
      "spec_version":    "1.1.0",
      "payload": {
        "event_id":      "<UUID v4>",
        "event_type":    "pricing.price_updated",
        "created_at":    "2026-05-29T14:30:00Z",
        "region_code":   "KE-30",
        "sku_code":      "TOMATO_GRADE_A",
        "window":        "30d",
        "sample_size":   142
      }
    }
  ],
  "next_page_token": "<opaque>"
}
```

Each row mirrors the bytes the server would have POSTed in a live
delivery, allowing the receiver to verify the signature against
`payload` as if it had been delivered live.

### New OAuth scope

`events:read` — read access to historical event deliveries for the
client's own subscriptions.

### Retention

Servers MUST retain events for at least **30 days**. `since` older than
30 days returns `400 invalid_request` with detail "since older than
retention window".

## Alternatives considered

1. **Increase the live-retry budget to 7 days.** Rejected: balloons
   the server's pending-delivery queue size and still misses
   2-week outages (common in rural Kenya / TZ with grid issues).
2. **Receiver maintains a sliding window of expected event_ids and
   pulls them individually.** Rejected: requires a separate `GET
   /v1/events/{event_id}` endpoint per missed event, multiplying RTT
   for receivers that missed many events.

## Backwards compatibility

**MINOR**. Net-new endpoint + scope. Existing v1.0 clients are
unaffected.

## Open questions

- [ ] Should the retention be tenant-tunable via Privacy Manifest?
      → Decided: NO, retention is fixed at 30d in v1.1; future RFC may
      add it as a manifest field if implementers request it.

## First-implementer commitment

2Africa AgriCloud will ship the endpoint in v1.1 along with the spec
release.
