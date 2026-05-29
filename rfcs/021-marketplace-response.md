<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# RFC-021: In-Protocol Marketplace Response

| Field             | Value                                   |
| ----------------- | --------------------------------------- |
| Status            | Accepted                                |
| Author            | 2Africa OpenAPI Maintainers             |
| Created           | 2026-05-29                              |
| Comment window    | 14 days from Open                       |
| Target version    | v1.1                                    |
| First implementer | 2Africa AgriCloud v1.1                  |

## Problem

v1.0 lets a seller-side client *read* marketplace orders
(`GET /v1/downstream/marketplace`) but offers no protocol-defined way
to *respond*. The endpoint description acknowledges this:

> "Posting a response is OUT of scope for v1.0 (see RFC-021 for the
> v1.1 proposal)."

In practice, sellers respond out-of-band (phone, WhatsApp, email),
which:

- breaks the audit trail (no `request_id` correlation),
- defeats the Privacy Manifest model (out-of-band channels bypass the
  declared allow-list),
- forces every implementer to invent their own response shape, undoing
  the standard.

## Proposal

Add a new downstream sub-endpoint:

```
POST /v1/downstream/marketplace/{order_id}/responses
```

### Request

```json
{
  "seller_pseudo_id":      "<UUID v4>",
  "offered_quantity":      { "quantity": 5000, "unit": "kg" },
  "offered_unit_price":    { "amount": "78.50", "currency": "KES" },
  "available_from":        "2026-06-01",
  "available_until":       "2026-06-10",
  "notes":                 "Free delivery within KE-30 for orders ≥ 1 t."
}
```

Mandatory headers identical to other downstream POSTs:
`Authorization`, `X-Spec-Version`, `Idempotency-Key`.

### Response (`201 Created`)

```json
{
  "response_id":   "<UUID v4>",
  "order_id":      "<UUID v4>",
  "accepted_at":   "2026-05-29T14:30:00Z",
  "buyer_notified": true
}
```

### New OAuth scope

`marketplace:respond` — submit responses to marketplace orders. NOT
implied by `downstream:marketplace` (which is read-only); a token
needing both must request both scopes.

### Webhook

After acceptance, the server SHOULD deliver
`marketplace.response_received` to the *buyer* (a new webhook event
added in this RFC).

### Server obligations

- Reject (`410 Gone`) if the order has expired.
- Reject (`409 Conflict`) if the same `seller_pseudo_id` already
  responded to the same `order_id`.
- The response payload is visible only to the originating buyer and
  the responding seller — NOT broadcast in subsequent
  marketplace listings.

## Alternatives considered

1. **POST to a top-level `/v1/marketplace/responses`** without the
   path-nested `order_id`. Rejected: less RESTful, harder to write
   path-based rate limits and audit queries.
2. **Reuse `/v1/upstream/marketplace-responses`**. Rejected: this is
   not upstream business data — it's a downstream interaction. Putting
   it under `/v1/upstream` would confuse the Privacy Manifest's
   per-endpoint policy semantics.

## Backwards compatibility

**MINOR**. Net-new endpoint, net-new scope, net-new webhook event.
Existing v1.0 clients are unaffected.

## Open questions

- [ ] Should the seller's contact info (phone / email) be included in
      the response payload? → Decided: NO in v1.1. The buyer initiates
      contact through the platform's UI; the protocol stays
      identifier-only.

## First-implementer commitment

2Africa AgriCloud will ship the endpoint + the
`marketplace.response_received` webhook in v1.1.
