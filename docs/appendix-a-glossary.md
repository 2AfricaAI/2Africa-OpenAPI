<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# Appendix A · Glossary

| Term                    | Meaning                                                                |
| ----------------------- | ---------------------------------------------------------------------- |
| **AsyncAPI 2.6**        | The IDL used to describe the webhook channels in `spec/webhooks.asyncapi.yaml`. |
| **Batch**               | A single POST containing multiple records, e.g. yields.                |
| **Client**              | The party initiating a request — usually farm-side.                    |
| **Conformance level**   | L1 / L2 / L3 as defined in chapter 1 §1.3.                             |
| **Cursor pagination**   | Opaque `next_page_token`; no offset/limit (§3.7).                      |
| **Data owner**          | The legal natural or legal person whose business data is described.    |
| **Downstream**          | Server-to-client direction (chapter 6).                                |
| **EndpointPolicy**      | One per upstream endpoint inside the Privacy Manifest (chapter 4).     |
| **Idempotency-Key**     | UUID v4 per logical operation; servers dedupe ≥ 24 h (§3.8).           |
| **Implementer**         | An organisation shipping a server or client conformant to this spec.   |
| **JWT**                 | JSON Web Token (RFC 7519). Access tokens are JWTs (§2.5).              |
| **L1 / L2 / L3**        | Conformance levels (§1.3).                                             |
| **OAuth 2.0 + PKCE**    | The authentication framework (chapter 2).                              |
| **OpenAPI 3.1**         | The IDL used for HTTP endpoints in `spec/openapi.yaml`.                |
| **Platform**            | The party fulfilling requests — typically multi-tenant.                |
| **Privacy Manifest**    | Owner-authored YAML declaring per-endpoint field allow-lists (chapter 4). |
| **PRD**                 | Product Requirements Document — internal draft, not the standard.      |
| **Problem (RFC 7807)**  | Error body shape for HTTP errors (chapter 8).                          |
| **Region code**         | `<ISO 3166-1>-<ISO 3166-2>` (§3.6).                                    |
| **RFC 2119**            | The keywords MUST / SHOULD / MAY are interpreted per this RFC.         |
| **Sample-size floor**   | Servers MUST NOT return aggregated rows where `sample_size < 30` (§3.10). |
| **SemVer 2.0.0**        | Versioning discipline; chapter 1 §1.1.                                 |
| **SKU**                 | Stock Keeping Unit — a graded saleable variant of a crop.              |
| **Tenant**              | A single farm or agricultural enterprise.                              |
| **tenant_pseudo_id**    | Stable, non-reversible pseudonym per tenant per server (§3.5).         |
| **Upstream**            | Client-to-server direction (chapter 5).                                |
| **Webhook**             | Server-to-client push notification (chapter 7).                        |
| **X-AgriCloud-Signature** | HMAC-SHA256 header on webhook deliveries (§7.4).                     |
| **X-Privacy-Manifest-Hash** | SHA-256 of the owner's published Manifest (§4.3).                  |
| **X-Spec-Version**      | SemVer of the spec the client implements (§1.2).                       |
