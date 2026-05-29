<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# 1 · Versioning & Conformance

## 1.1 SemVer 2.0.0

The specification follows [SemVer 2.0.0](https://semver.org/) strictly.

| Increment | When                                              | Example          |
| --------- | ------------------------------------------------- | ---------------- |
| **MAJOR** | Breaking change. Old clients may not interoperate. | `1.0.0` → `2.0.0` |
| **MINOR** | Backwards-compatible addition (new field, new endpoint, new scope). | `1.0.0` → `1.1.0` |
| **PATCH** | Editorial fix — wording, example, error message. No wire change. | `1.0.0` → `1.0.1` |

Pre-release suffixes (`-rc1`, `-rc2`) precede a final release but are
considered stable enough for integration testing.

## 1.2 Wire-level version negotiation

Every request **MUST** carry an `X-Spec-Version` HTTP header:

```http
X-Spec-Version: 1.0.0-rc1
```

Servers SHOULD respond with their own `X-Spec-Version` header so the
client knows which version of the contract was honoured.

If client and server disagree on MAJOR version, the server MUST reject
with `400 invalid_request` and a Problem `detail` field that names the
supported MAJOR versions.

## 1.3 Conformance levels

| Level        | Required                                                       | Target implementer  |
| ------------ | -------------------------------------------------------------- | ------------------- |
| **L1 Basic** | OAuth + at least 1 upstream endpoint + Privacy Manifest        | AgriOS v3.4         |
| **L2 Full**  | All 10 upstream + downstream endpoints + signed webhook delivery | AgriCloud v1.0    |
| **L3 Adv.**  | L2 + end-to-end field-level encryption + federated identity    | future (v2.0+)      |

A client may advertise its level in the `X-Conformance-Level` request
header. A server may include `X-Server-Conformance-Level` in its
responses. Neither is required; both are useful for integration
diagnostics.

## 1.4 Deprecation policy

Any field, endpoint, scope, or error code being removed MUST:

1. Be labelled `DEPRECATED` in the spec for **at least 12 months**
   before removal.
2. Emit `Deprecation: true` and `Sunset: <RFC 7231 HTTP date>` HTTP
   headers on every response touching the deprecated surface.
3. Have a documented equivalent replacement (if any).
4. Be removed only in the next MAJOR release **after** the 12-month
   window elapses.

Example response from a server still honouring a deprecated endpoint:

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Wed, 29 May 2027 00:00:00 GMT
Link: <https://openapi.2africa.ai/docs/migrations/v1-to-v2>; rel="deprecation"
```

## 1.5 What is and is not a breaking change

| Change                                                  | Bump   |
| ------------------------------------------------------- | ------ |
| Add optional field                                      | MINOR  |
| Add required field with safe default                    | MINOR  |
| Add new endpoint                                        | MINOR  |
| Add new scope                                           | MINOR  |
| Add new error code                                      | MINOR  |
| Loosen validation (previously-rejected input accepted)  | MINOR  |
| Tighten validation (previously-accepted input rejected) | MAJOR  |
| Remove field / endpoint / scope                         | MAJOR  |
| Rename field                                            | MAJOR  |
| Change semantics of existing field                      | MAJOR  |
| Change HTTP status code for an existing error condition | MAJOR  |
| Change authentication flow                              | MAJOR  |

## 1.6 Governance of changes

Substantive changes go through the [RFC process described in
GOVERNANCE.md §2.2](../GOVERNANCE.md#22-substantive-changes--rfc-process):

1. RFC PR opened against `rfcs/NNN-title.md`.
2. 14-day public comment window.
3. At least two maintainer approvals + no unresolved blocker from a
   known implementer.
4. Spec PR + CHANGELOG entry merged separately.
5. Next MINOR (or MAJOR) release ships the change.
