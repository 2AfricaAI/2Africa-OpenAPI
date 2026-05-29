<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# 0 · Overview

## What this is

**2Africa OpenAPI** is an open, versioned, vendor-neutral specification
that defines how single-farm operating systems (such as
[2Africa AgriOS](https://github.com/2AfricaAI/2Africa-AgriOS)) and
multi-tenant agricultural platforms (such as 2Africa AgriCloud,
Cropin, Apollo Agriculture, banks, certifiers, NGOs, and government
ag-data systems) exchange data with each other.

The standard covers:

- How a farm-side client safely **pushes** anonymous data to a
  platform (yields, prices, GAP audits, credit packs, telemetry).
- How a platform safely **pushes** notifications and downstream
  reference data back to the farm (dictionaries, regional prices,
  benchmarks, marketplace orders, group-buy opportunities).
- How an end-user data owner **controls** what travels over the wire
  through a Privacy Manifest.
- How authentication, signatures, error codes, and version
  negotiation work across all of the above.

## What this is not

- ❌ A product. Implementations live in other repositories.
- ❌ A database schema. It only defines what travels over the wire.
- ❌ A commercial agreement. Commercial terms are negotiated
  separately between implementers and their customers.

## Who should read which chapter

| If you are…                            | Start at                                              |
| -------------------------------------- | ----------------------------------------------------- |
| A farm-management vendor               | [05 Upstream](./05-upstream.md)                       |
| A bank / insurer / certifier           | [06 Downstream](./06-downstream.md)                   |
| A platform building federation         | [02 Auth](./02-auth.md), [07 Webhooks](./07-webhooks.md) |
| A farmer choosing software             | [04 Privacy](./04-privacy.md)                         |
| A regulator                            | [10 Compliance](./10-compliance.md)                   |
| An SDK author                          | [09 SDKs](./09-sdks.md), [08 Errors](./08-errors.md)  |
| A specification reviewer               | read in order                                         |

## Key design principles

1. **Vendor-neutral.** No clause in the spec assumes any particular
   server implementation. Both AgriOS and AgriCloud must implement
   the spec; neither *is* the spec.
2. **Privacy first.** All upstream endpoints are OFF by default. A
   Privacy Manifest is required and cryptographically attested on
   every upstream call.
3. **Aggregate, never identify.** Server responses MUST NOT return
   any row whose sample size is below 30. Region codes do not go
   below the second ISO 3166 level.
4. **Industry boring.** OAuth 2.0, JWT, RFC 7807, ISO 8601, ISO 4217,
   UUID v4 — no homemade primitives where a public RFC exists.
5. **Forward-compatible.** Clients send `X-Spec-Version`. Servers
   may shim minor differences but never silently change semantics.
6. **Cursor-only.** No `offset` / `limit`. Page tokens are opaque to
   the client.

## Reading conventions

| Term       | Meaning                                            |
| ---------- | -------------------------------------------------- |
| **MUST**   | RFC 2119 requirement.                              |
| **SHOULD** | RFC 2119 recommendation.                           |
| **MAY**    | RFC 2119 optional.                                 |
| Client     | The party initiating a request (often farm-side).  |
| Server     | The party fulfilling a request (often platform).   |
| Tenant     | A single farm (or agricultural enterprise).        |

Code samples are illustrative; the authoritative machine-readable
form is [`spec/openapi.yaml`](../spec/openapi.yaml).
