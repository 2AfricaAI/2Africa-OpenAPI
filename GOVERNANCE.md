<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# Governance

This document describes how the 2Africa OpenAPI specification is
maintained and how decisions are made.

The standard is intended to outlast any single implementer. The goal of
this governance is **predictability for implementers** more than speed
of iteration.

---

## 1 · Stewardship

The specification is currently stewarded by **2Africa AI** (the original
authors) as the sole maintainer of the GitHub repository
<https://github.com/2AfricaAI/2Africa-OpenAPI>.

Stewardship will transition to a multi-vendor **OpenAPI Steering
Committee** (see §5) once at least three independent organisations have
shipped a conformant implementation in production.

---

## 2 · Decision-making

### 2.1 Trivial changes — Maintainer merge

Editorial fixes (typos, broken links, clarifications that do not change
semantics) may be merged by a maintainer after one approving review and
all CI checks passing.

### 2.2 Substantive changes — RFC process

Any change to the wire protocol — new endpoint, new field, semantic
change to an existing field, change to authentication, change to error
codes, change to conformance levels — **must** go through an RFC.

```
   IDEA  ──→  RFC draft (PR to /rfcs/NNN-title.md)
                   │
                   ▼
            14-day public comment
                   │
            ┌──────┴──────┐
            ▼             ▼
          ACCEPT       REJECT
            │
            ▼
       spec update PR + CHANGELOG entry
            │
            ▼
        merge → next MINOR or MAJOR release
```

The 14-day comment window starts when the RFC PR is opened and labelled
`rfc:open`. Comments may be submitted by anyone via PR review or issue
reference. To accept, the RFC must:

- have at least **two** approvals from maintainers / committee members,
- have **no unresolved blocking objection** from a known production
  implementer,
- pass CI (`spec-lint`, `markdown-lint`).

### 2.3 Emergency security changes

A maintainer may merge a security fix without the 14-day window if:

- it closes a vulnerability disclosed via [SECURITY.md](./SECURITY.md),
- it does not introduce new endpoints or fields,
- it is followed within 7 days by a retroactive RFC describing the
  threat model and the fix.

---

## 3 · Versioning & release

Strict [SemVer 2.0.0](https://semver.org/). Release cadence:

| Type      | Cadence    | Examples                                     |
| --------- | ---------- | -------------------------------------------- |
| PATCH     | as needed  | typo fixes, clarifications, error-msg fixes  |
| MINOR     | quarterly  | new fields, new endpoints, new scopes        |
| MAJOR     | yearly max | breaking changes (re-shaped JSON, new auth)  |

### 3.1 Deprecation policy

Any field, endpoint, scope, or error code being removed must:

1. Carry the label `DEPRECATED` in the spec for **at least 12 months**.
2. Emit a `Deprecation:` and `Sunset:` HTTP header on every response
   touching the deprecated surface.
3. Have a documented equivalent replacement (if any).
4. Be removed only in the next MAJOR release after the 12-month window.

### 3.2 What counts as a breaking change

| Change                                                  | Bump  |
| ------------------------------------------------------- | ----- |
| Add optional field                                      | MINOR |
| Add required field with default behaviour preserved     | MINOR |
| Add new endpoint                                        | MINOR |
| Add new scope                                           | MINOR |
| Add new error code                                      | MINOR |
| Tighten validation (previously-accepted input rejected) | MAJOR |
| Remove field / endpoint / scope                         | MAJOR |
| Rename field                                            | MAJOR |
| Change semantics of existing field                      | MAJOR |
| Change HTTP status code for an error condition          | MAJOR |

---

## 4 · Implementer registry

To keep the ecosystem visible, every organisation shipping a conformant
implementation in production is invited to add itself to
`docs/implementers.md` (Sprint 1+) via a PR including:

- name, homepage, contact email
- claimed conformance level (L1 / L2 / L3)
- date first conformant
- link to public confirmance test report (if any)

Self-declared. The Steering Committee may audit on request.

---

## 5 · Steering Committee (forming)

Composition target:

- **2 seats** — original stewards (2Africa AI)
- **3 seats** — independent implementers (rotating, 2-year term)
- **1 seat** — non-implementer ecosystem rep (regulator, NGO,
  academic — advisory voice, voting on user-facing changes only)

Meetings: quarterly, public minutes, asynchronous voting acceptable.
Quorum: 4 of 6 seats.

The committee will be convened once the criteria in §1 are met. Until
then, the original stewards act as the de-facto committee with the same
RFC process applied transparently.

---

## 6 · Trademark

"2Africa OpenAPI" is a project name, not a certification mark. Anyone
may claim conformance to a specific version (e.g. "OpenAPI 1.0 L2
compliant") without permission, provided they truthfully meet the
conformance criteria.

A formal certification mark may be introduced in a future MAJOR
release.

---

## 7 · Amendment of this document

GOVERNANCE.md itself follows the RFC process (§2.2). Changes to the
RFC process require a **30-day** comment window (longer than ordinary
RFCs).

---

*Last revised: 2026-05-29 — v0.1.0-skeleton.*
