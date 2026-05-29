<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# 2Africa OpenAPI

> The open federation protocol for African agricultural data exchange.
> A vendor-neutral standard — not a product.

[![Spec License: CC BY 4.0](https://img.shields.io/badge/spec-CC%20BY%204.0-lightgrey.svg)](./LICENSE-spec)
[![SDK License: Apache 2.0](https://img.shields.io/badge/sdk-Apache%202.0-blue.svg)](./LICENSE-sdk)
[![Spec Lint](https://github.com/2AfricaAI/2Africa-OpenAPI/actions/workflows/spec-lint.yml/badge.svg)](https://github.com/2AfricaAI/2Africa-OpenAPI/actions/workflows/spec-lint.yml)
[![Docs Lint](https://github.com/2AfricaAI/2Africa-OpenAPI/actions/workflows/markdown-lint.yml/badge.svg)](https://github.com/2AfricaAI/2Africa-OpenAPI/actions/workflows/markdown-lint.yml)

---

## What this is

**2Africa OpenAPI** is an open, versioned, vendor-neutral specification
that defines how single-farm operating systems (such as
[2Africa AgriOS](https://github.com/2AfricaAI/2Africa-AgriOS)) and
multi-tenant agricultural platforms (such as 2Africa AgriCloud,
Cropin, Apollo Agriculture, banks, certifiers, NGOs, and government
ag-data systems) exchange data with each other.

It is to African ag-data what:

| HTTP        | is to web pages         |
| ----------- | ----------------------- |
| OAuth       | is to login             |
| SMTP        | is to email             |
| OFX / FDX   | is to bank data         |
| **OpenAPI** | **is to farm data**     |

This repository **is** the standard. It is not owned by any single
implementer.

## What this is not

- ❌ Not a product. Implementations live in other repositories.
- ❌ Not a database schema. It only defines what travels over the wire.
- ❌ Not a commercial agreement. Commercial terms are negotiated
  separately between implementers and their customers.

## Who should read this

| If you are…                                  | Start at                                |
| -------------------------------------------- | --------------------------------------- |
| A farm-management vendor                     | [`docs/upstream.md`](./docs/upstream.md) (when written) |
| A bank / insurer / certifier                 | [`docs/downstream.md`](./docs/downstream.md) (when written) |
| A platform building federation               | [`docs/auth.md`](./docs/auth.md) (when written) |
| An end-user farmer choosing software         | [`docs/privacy.md`](./docs/privacy.md) (when written) |
| A regulator                                  | [`docs/compliance.md`](./docs/compliance.md) (when written) |
| An SDK consumer                              | [`sdks/`](./sdks)                       |

> Note: the per-chapter Markdown files are scheduled for **Sprint 1**.
> Until then the canonical source is the OpenAPI 3.1 YAML in
> [`spec/openapi.yaml`](./spec/openapi.yaml).

## Repository layout

```
.
├── spec/                          OpenAPI 3.1 + AsyncAPI 2.6 + JSON Schema
│   ├── openapi.yaml               main HTTP API (10 endpoints, Sprint 1)
│   ├── privacy-manifest.schema.yaml   Privacy Manifest format (Sprint 1)
│   └── webhooks.asyncapi.yaml         webhook event channel (Sprint 1)
├── docs/                          long-form docs (8–10 chapters, Sprint 1)
├── sdks/
│   ├── java/                      reference Java SDK   (Sprint 2)
│   ├── python/                    reference Python SDK (Sprint 2)
│   └── javascript/                reference JS/TS SDK  (Sprint 2)
├── examples/                      Postman + curl + manifest samples
├── tests/                         compliance test suite (CTS)
├── .github/workflows/             Spectral + markdown-lint CI
├── LICENSE-spec                   CC BY 4.0 (covers spec/ and docs/)
├── LICENSE-sdk                    Apache-2.0 (covers sdks/, examples/, tests/)
├── NOTICE                         attribution & dual-license summary
├── GOVERNANCE.md                  RFC process & Steering Committee
├── CONTRIBUTING.md                how to propose changes
├── CODE_OF_CONDUCT.md             behaviour expected of contributors
├── SECURITY.md                    how to report vulnerabilities
└── CHANGELOG.md                   versioned change log
```

## Design at a glance

| Concern              | Choice                                                 |
| -------------------- | ------------------------------------------------------ |
| Auth                 | OAuth 2.0 + PKCE (RFC 6749 + 7636), JWT access tokens  |
| Errors               | RFC 7807 Problem Details                               |
| Field names          | `snake_case`                                           |
| Time                 | ISO 8601 UTC, no local time, no relative time          |
| Money                | `amount` + `currency` (ISO 4217), 2-decimal            |
| IDs                  | UUID v4; `tenant_pseudo_id` for stable pseudonymity    |
| Pagination           | Cursor-based, never `offset` / `limit`                 |
| Region codes         | `<ISO 3166-1>-<ISO 3166-2>` (e.g. `KE-30` = Nairobi)   |
| Privacy              | Privacy Manifest, SHA-256 hash header per request      |
| Webhooks             | HMAC-SHA256 signature, 5-step exponential backoff      |

## Endpoints (10)

**5 Upstream** (single-farm → platform, all OFF by default):

| Method | Path                            | Purpose                            |
| ------ | ------------------------------- | ---------------------------------- |
| POST   | `/v1/upstream/yields`           | anonymous harvest yields           |
| POST   | `/v1/upstream/prices`           | anonymous sale prices              |
| POST   | `/v1/upstream/gap-records`      | GAP audit records                  |
| POST   | `/v1/upstream/credit-pack`      | one-shot credit pack for banks     |
| POST   | `/v1/upstream/telemetry`        | anonymous usage telemetry (opt-in) |

**5 Downstream** (platform → single-farm, ON by default):

| Method | Path                            | Purpose                       |
| ------ | ------------------------------- | ----------------------------- |
| GET    | `/v1/downstream/dictionaries`   | standard crop / SKU / region  |
| GET    | `/v1/downstream/prices`         | regional price benchmarks     |
| GET    | `/v1/downstream/benchmarks`     | peer benchmarks               |
| GET    | `/v1/downstream/marketplace`    | sourcing orders               |
| GET    | `/v1/downstream/procurement`    | group-buy opportunities       |

## Conformance levels

| Level       | Requirements                                                       | Target implementer            |
| ----------- | ------------------------------------------------------------------ | ----------------------------- |
| **L1 Basic**| OAuth + ≥1 upstream endpoint + Privacy Manifest                    | AgriOS v3.4                   |
| **L2 Full** | All 10 endpoints + Webhook delivery                                | AgriCloud v1.0                |
| **L3 Adv.** | L2 + end-to-end field-level encryption + federated identity        | future (v2.0+)                |

## Versioning

Strict [SemVer 2.0.0](https://semver.org/). Deprecations carry a
**12-month sunset window** and ship with `Deprecation:` + `Sunset:`
HTTP headers.

## Dual license

| Tree                     | License        | Why                                                |
| ------------------------ | -------------- | -------------------------------------------------- |
| `spec/**`, `docs/**`     | **CC BY 4.0**  | document-style: attribution required, no patents   |
| `sdks/**`, `examples/**`, `tests/**` | **Apache-2.0** | code-style: explicit patent grant, frictionless reuse |

See [LICENSE-spec](./LICENSE-spec), [LICENSE-sdk](./LICENSE-sdk), and
[NOTICE](./NOTICE).

## Status

This is a **pre-release skeleton** (`v0.1.0-skeleton`).

| Milestone                                 | ETA              |
| ----------------------------------------- | ---------------- |
| `v0.1.0-skeleton` — Sprint 0 done         | now              |
| `v1.0.0-rc1`     — Sprint 1 spec complete | +3–4 days        |
| `v1.0.0`         — public spec freeze     | shortly after rc |
| `v1.0.0` SDKs published (Maven / PyPI / npm) — Sprint 2 | +3 days   |

## Get involved

- Propose a change: read [GOVERNANCE.md](./GOVERNANCE.md) (RFC process)
- Open an issue: <https://github.com/2AfricaAI/2Africa-OpenAPI/issues>
- Security: see [SECURITY.md](./SECURITY.md)
- Code of conduct: [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)

## Reference implementations

| Side     | Repo                                                                 | Status         |
| -------- | -------------------------------------------------------------------- | -------------- |
| Client   | [2Africa AgriOS](https://github.com/2AfricaAI/2Africa-AgriOS)        | v3.4 → L1, v3.5 → L2 |
| Server   | 2Africa AgriCloud                                                    | v1.0 → L2 (closed-source) |
| Sandbox  | `https://sandbox.agricloud.2africa.ai` (free, 7-day token renewal)   | post-v1.0      |

Third-party implementers welcome — see the
[compatibility test suite](./tests) (Sprint 1+).

---

© 2026 2Africa AI and OpenAPI Contributors. Specification under CC BY 4.0,
SDKs under Apache-2.0.
