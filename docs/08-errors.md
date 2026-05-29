<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# 8 · Errors & Status

## 8.1 RFC 7807 Problem Details

All error responses use
[RFC 7807](https://datatracker.ietf.org/doc/html/rfc7807) Problem
Details, content type `application/problem+json`.

Skeleton body:

```json
{
  "type":       "https://errors.2africa.ai/invalid-token",
  "title":      "Unauthorized",
  "status":     401,
  "detail":     "Access token expired 12 seconds ago; refresh and retry.",
  "instance":   "/v1/upstream/yields",
  "request_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

Required fields: `type`, `title`, `status`. All others are SHOULD.
Servers MAY add extension members; clients MUST tolerate unknown
keys.

## 8.2 Error catalogue (v1.0)

| `type` URL suffix             | Status | Title                | When                                                  |
| ----------------------------- | -----: | -------------------- | ----------------------------------------------------- |
| `invalid-request`             |    400 | Bad Request          | Malformed body, missing required header, invalid enum |
| `version-mismatch`            |    400 | Bad Request          | `X-Spec-Version` MAJOR differs from server            |
| `invalid-token`               |    401 | Unauthorized         | Token missing / expired / signature invalid           |
| `insufficient-scope`          |    403 | Forbidden            | Token authentic but lacks required scope              |
| `not-found`                   |    404 | Not Found            | Resource not found or filtered by privacy guard       |
| `idempotency-conflict`        |    409 | Conflict             | Same `Idempotency-Key`, different body                |
| `manifest-hash-mismatch`      |    422 | Unprocessable Entity | Server's cached manifest hash != request header       |
| `manifest-field-not-allowed`  |    422 | Unprocessable Entity | A field in the body is outside the manifest allow-list |
| `rate-limited`                |    429 | Too Many Requests    | Quota exceeded                                        |
| `service-unavailable`         |    503 | Service Unavailable  | Server is draining or downstream impaired             |

`type` URLs are stable across MINOR versions. They are documentation
landing pages, NOT API endpoints — fetching them returns human-
readable HTML explaining the error and its remediation.

## 8.3 Field-level validation errors

For batch endpoints, `detail` SHOULD include a JSON pointer to the
offending field:

```json
{
  "type":   "https://errors.2africa.ai/invalid-request",
  "title":  "Bad Request",
  "status": 400,
  "detail": "records[2].quantity.unit: must be one of kg, ton, crate, bag_25kg, bag_50kg, litre, dozen, head"
}
```

A future MINOR will introduce an `errors[]` extension member listing
multiple per-record errors; v1.0 returns only the first.

## 8.4 Replays and partial success

| Situation                                          | Behaviour                                          |
| -------------------------------------------------- | -------------------------------------------------- |
| Retry within the dedupe window, same body          | 2xx with `Idempotency-Replay: true` and the original body |
| Retry within the dedupe window, different body     | `409 idempotency-conflict`; original outcome is preserved |
| Partial batch acceptance (e.g. 1 of 5 records bad) | 202 with `accepted_count` < submitted; rejection details TBD in v1.1 |

## 8.5 Rate limiting

Rate limits are applied per `client_id` and per scope. Default
ceilings (servers MAY tighten):

| Scope                       | Default                |
| --------------------------- | ---------------------- |
| `privacy:manage`            |    10 req/min          |
| `upstream:yields`           |  1 000 req/h           |
| `upstream:prices`           |  1 000 req/h           |
| `upstream:gap`              |    200 req/h           |
| `upstream:credit-pack`      |     10 req/h           |
| `upstream:telemetry`        | 10 000 req/h           |
| `downstream:*`              |    600 req/min combined |

When a limit is exhausted:

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/problem+json
Retry-After: 47

{
  "type":   "https://errors.2africa.ai/rate-limited",
  "title":  "Too Many Requests",
  "status": 429,
  "detail": "Quota exhausted: 1000 calls / hour for upstream:yields."
}
```

`Retry-After` is in seconds. Clients MUST honour it.

## 8.6 Server-induced backoff

Servers MAY include `Retry-After` on any 5xx response. Clients
SHOULD respect it. If absent, clients SHOULD back off
exponentially starting at 1 second, capped at 60 s, with full
jitter.

## 8.7 What is *not* a 4xx

The following situations do not return errors in v1.0:

- An upstream batch with `accepted_count == 0` due to all records
  being deduped — that is `202` with `accepted_count: 0`.
- A downstream query that produces an empty page — that is `200`
  with `items: []`.
- A `system.healthcheck` webhook received twice — the second
  delivery returns 2xx (dedupe is silent).
- A token approaching expiry — clients refresh proactively; servers
  do not warn. (A future MINOR may add a `Token-Expiring:` header.)
