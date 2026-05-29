<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# Security Policy

This document describes how to report a vulnerability **in the
specification itself** — for example, a flaw in the authentication
flow, a missing replay defence, an under-specified signature
verification step, or a privacy leak that follows from the wire
contract.

> If you find a vulnerability in a specific **implementation**
> (AgriOS, AgriCloud, a third-party server), please contact that
> implementer directly. AgriOS issues go to `security@2africa.ai`
> referencing AgriOS. AgriCloud production issues go to
> `security@2africa.ai` referencing AgriCloud.

---

## 1 · Reporting a vulnerability

**Do NOT open a public GitHub issue.**

Email **security@2africa.ai** with the following:

- A clear description of the issue
- Steps to reproduce (sample requests, sample manifest, etc.)
- The version of the spec affected (e.g. `v1.0.0`)
- Your suggested fix, if any
- Whether you would like public credit upon disclosure

You should receive an acknowledgement within **3 business days**.

For sensitive reports, our PGP key fingerprint will be published at
`https://2africa.ai/.well-known/security.txt` once production
infrastructure is online. Until then, please email plain text and we
will arrange a secure channel on first response.

## 2 · Coordinated disclosure timeline

| Stage                                              | Target               |
| -------------------------------------------------- | -------------------- |
| Acknowledge receipt                                | within 3 days        |
| Initial assessment shared with reporter            | within 14 days       |
| Fix (or interim mitigation) drafted                | within 60 days       |
| Coordinated public disclosure                      | within 90 days       |
| Credit reporter in CHANGELOG and advisory          | on disclosure (opt-in) |

If we cannot meet a milestone, we will tell the reporter why and
propose a new date.

## 3 · What counts as a vulnerability in the spec

- An authentication flow that allows token replay, downgrade, or
  forgery.
- A signature scheme that does not bind to the request body or
  timestamp.
- A privacy manifest semantics that fails to block sensitive fields it
  claims to block.
- An error response that leaks data not authorised by the requesting
  scope.
- A webhook delivery mechanism that allows unauthorised parties to
  inject events.
- Any flow whose plain reading of the spec produces an insecure
  implementation.

A *correctly* documented insecure choice that is intentional (e.g. the
opt-in telemetry endpoint) is **not** a vulnerability.

## 4 · Safe harbour

We will not pursue civil or criminal action against good-faith security
researchers who:

- Make a reasonable effort to avoid privacy violations, destruction of
  data, and interruption of services.
- Use only the official sandbox (`sandbox.agricloud.2africa.ai`, when
  available) to demonstrate vulnerabilities. Do not test against
  production implementations without explicit written permission.
- Report the issue to us before public disclosure.
- Do not extort, threaten, or condition disclosure on payment.

## 5 · Out of scope

- Implementation-specific issues (report to the implementer).
- Issues that require physical access to a contributor's machine.
- Social-engineering attacks against contributors.
- Denial-of-service attacks at the network or transport layer (these
  are infrastructure concerns, not spec concerns).

## 6 · Hall of fame

Once the project has received its first acknowledged disclosure, we
will maintain a `SECURITY-HALL-OF-FAME.md` listing reporters who have
opted in for credit.

---

*Last revised: 2026-05-29 — v0.1.0-skeleton.*
