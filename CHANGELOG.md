<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# Changelog

All notable changes to the 2Africa OpenAPI specification are recorded
here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versioning follows [SemVer 2.0.0](https://semver.org/).

The spec uses the **`Deprecation:`** and **`Sunset:`** HTTP headers to
signal upcoming removals; deprecations also appear in this log under a
`Deprecated` heading 12 months before removal.

---

## [Unreleased]

### Added

- Nothing yet.

### Changed

- Nothing yet.

### Deprecated

- Nothing yet.

### Removed

- Nothing yet.

### Fixed

- Nothing yet.

### Security

- Nothing yet.

---

## [1.1.0-rc1] — 2026-05-29

Second release candidate. Two new endpoints land via the formal RFC
process — first end-to-end exercise of GOVERNANCE.md §2.2.

### Added

- **RFC-019**: `GET /v1/events?since=<unix_seconds>` — webhook backfill
  endpoint. Retention ≥ 30 days. New scope `events:read`. Rows mirror
  live-delivery bytes for identical signature verification. Closes the
  receiver-offline-beyond-24h gap noted in v1.0 webhooks.asyncapi.yaml.
- **RFC-021**: `POST /v1/downstream/marketplace/{order_id}/responses` —
  in-protocol marketplace response. New scope `marketplace:respond`
  (NOT implied by `downstream:marketplace`). New webhook event
  `marketplace.response_received` delivered to the buyer.
- 4 new component schemas: EventReplayRow, EventReplayPage,
  MarketplaceResponse, MarketplaceResponseAck.
- 2 new OAuth scopes wired into authorizationCode flow.
- docs: §6.5.1 marketplace response, §7.7 + §7.7.1 webhook backfill,
  §2.4 scope table updates.
- SDKs: `client.events.since(since)` + `client.marketplace_responses.respond(order_id, ...)`
  in both Python (`twoafrica-openapi==1.1.0rc1`) and JS (`@2africa/openapi@1.1.0-rc1`).
- CTS: 2 new L2 tests covering the new endpoints.
- `rfcs/` directory established with template + RFC-019 + RFC-021.

### Changed

- spec/openapi.yaml: 12 → 14 paths, 23 → 27 schemas, 11 → 13 scopes.
- Conformance L2 description now reads "all 12 endpoints + signed
  webhook delivery + event backfill".

### Backwards compatibility

Pure MINOR. No existing v1.0 client is broken. New endpoints + scopes
are additive; existing endpoints' wire shape is unchanged.

---

## [1.0.0-rc1] — 2026-05-29

First release candidate of the v1.0 specification. The wire contract
is now substantively complete; only editorial fixes and
implementation feedback should arrive before `v1.0.0`.

### Added

- `spec/openapi.yaml` (OpenAPI 3.1, 1091 lines):
  - 12 paths: `/healthz`, `PUT /v1/privacy-manifest`, five upstream
    POSTs, five downstream GETs.
  - 23 component schemas (HealthStatus, Problem, TenantPseudoId,
    RegionCode, Money, Quantity, YieldRecord, PriceRecord, GapRecord,
    CreditPack, CreditPackAck, TelemetryEvent, ManifestAck, BatchAck,
    DictionaryEntry, DictionaryPage, RegionalPrice, RegionalPricePage,
    Benchmark, MarketplaceOrder, MarketplaceOrderPage,
    ProcurementOpportunity, ProcurementOpportunityPage).
  - 7 reusable RFC 7807 error responses (400/401/403/404/409/422/429).
  - 5 reusable parameters (`X-Spec-Version`,
    `X-Privacy-Manifest-Hash`, `Idempotency-Key`, `page_token`,
    `page_size`).
  - 11 OAuth scopes across authorization_code + client_credentials
    flows.
- `spec/privacy-manifest.schema.yaml` (JSON Schema 2020-12, 164
  lines): per-endpoint `EndpointPolicy` (enabled, allow_fields,
  deny_fields, region_floor, retention_days, rate_limit_per_hour,
  recipients); profile presets strict / balanced / open / custom.
- `spec/webhooks.asyncapi.yaml` (AsyncAPI 2.6, 383 lines): six
  channels (system.healthcheck plus five production events:
  `pricing.price_updated`, `pricing.benchmark_refreshed`,
  `marketplace.order_posted`, `procurement.opportunity_opened`,
  `telemetry.config_changed`); shared EventHeaders + BaseEventPayload;
  HMAC-SHA256 signature, 5-minute replay window, five-step backoff.
- `docs/` (11 chapters + 2 appendices, 1 800+ lines):
  - 00 Overview, 01 Versioning & Conformance, 02 Auth (OAuth + PKCE),
  - 03 Data Conventions, 04 Privacy Manifest, 05 Upstream,
  - 06 Downstream, 07 Webhooks, 08 Errors, 09 SDKs, 10 Compliance,
  - Appendix A Glossary, Appendix B Implementer Registry.
- `examples/postman-collection.json` (Postman v2.1, 11 requests).
- `examples/curl/01-12-*.sh` — one shell script per endpoint.
- `examples/manifests/{strict,balanced,open}.yaml` — three reference
  Privacy Manifests aligned to `spec/privacy-manifest.schema.yaml`.
- `examples/webhook-replay/verify_signature.py` — reference HMAC
  verifier with self-test.
- `.github/workflows/docs-deploy.yml` — Redocly + GitHub Pages.

### Changed

- Root README badges bumped to v1.0.0-rc1 milestone.
- `.markdownlint.json` relaxed for the skeleton release; will be
  tightened alongside the real docs in v1.0.0.

### Security

- Mandatory 30-row sample-size floor on `/v1/downstream/prices`,
  `/v1/downstream/benchmarks` and the pricing webhook events to
  prevent re-identification.

---

## [0.1.0-skeleton] — 2026-05-29

Initial repository scaffold. Not a usable specification — bootstrap
only.

### Added

- Repository skeleton: `spec/`, `docs/`, `sdks/{java,python,javascript}/`,
  `examples/`, `tests/`, `.github/workflows/`.
- Dual license:
  - `LICENSE-spec` — CC BY 4.0 (covers `spec/`, `docs/`)
  - `LICENSE-sdk`  — Apache-2.0 (covers `sdks/`, `examples/`, `tests/`)
  - `NOTICE` — dual-license summary and third-party standard references
- Governance documents: README, GOVERNANCE (RFC process, 12-month
  deprecation), CONTRIBUTING, CODE_OF_CONDUCT (Contributor Covenant
  2.1), SECURITY (coordinated disclosure), CHANGELOG.
- Placeholder specs (real content in v1.0.0-rc1):
  - `spec/openapi.yaml` — `GET /healthz` only.
  - `spec/privacy-manifest.schema.yaml` — JSON Schema placeholder.
  - `spec/webhooks.asyncapi.yaml` — AsyncAPI 2.6 placeholder.
- Lint: `.spectral.yml` + `.markdownlint.json`.
- CI: `spec-lint.yml`, `markdown-lint.yml`.

[Unreleased]: https://github.com/2AfricaAI/2Africa-OpenAPI/compare/v1.1.0-rc1...HEAD
[1.1.0-rc1]: https://github.com/2AfricaAI/2Africa-OpenAPI/compare/v1.0.0-rc1...v1.1.0-rc1
[1.0.0-rc1]: https://github.com/2AfricaAI/2Africa-OpenAPI/compare/v0.1.0-skeleton...v1.0.0-rc1
[0.1.0-skeleton]: https://github.com/2AfricaAI/2Africa-OpenAPI/releases/tag/v0.1.0-skeleton
