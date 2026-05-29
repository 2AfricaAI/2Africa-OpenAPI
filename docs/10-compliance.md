<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# 10 · Compliance & Audit

## 10.1 Applicable law

The specification itself is jurisdiction-agnostic; specific
implementations are subject to:

| Jurisdiction (initial focus) | Relevant law                                          |
| ---------------------------- | ----------------------------------------------------- |
| Kenya                        | Data Protection Act 2019                              |
| Tanzania                     | Personal Data Protection Act 2022                     |
| Uganda                       | Data Protection and Privacy Act 2019                  |
| Senegal                      | Loi n° 2008-12                                        |
| EU (when applicable)         | GDPR — for European data subjects / banks             |

Conformant implementations MUST comply with the legal regime
applicable to the jurisdictions in which they operate. The wire
contract is designed to make compliance *possible*, not to relieve
implementers of the obligation.

## 10.2 Client-side audit logging

A conformant client MUST persist, for every upstream request, the
following fields locally for at least **365 days**:

| Field                       | Source                                       |
| --------------------------- | -------------------------------------------- |
| `timestamp`                 | The wall clock at request send.              |
| `endpoint`                  | The path, e.g. `/v1/upstream/yields`.        |
| `idempotency_key`           | The request header.                          |
| `manifest_hash`             | The request header.                          |
| `manifest_owner_id`         | From the active manifest body.               |
| `manifest_profile`          | From the active manifest body.               |
| `record_count`              | `len(records)` from the request body.        |
| `recipient_id` (credit-pack)| From the request body when applicable.       |
| `response_status`           | The HTTP status returned.                    |
| `server_request_id`         | From the Problem `request_id` or a response header. |

The owner can prove, from these logs alone, that no upstream call
exceeded what their Manifest permitted at the time of the call.

## 10.3 Right to be forgotten

A tenant may at any time request deletion of their upstream data
held by a platform:

1. Owner submits the request through the platform UI (out-of-band).
2. Platform MUST acknowledge in writing within 7 business days.
3. Platform MUST irreversibly delete the data and confirm with a
   tamper-evident certificate (PDF + JSON) including:
   - `tenant_pseudo_id`
   - `deleted_at`
   - SHA-256 of the deleted dataset bundle
   - signing key fingerprint
4. Platform MUST cease using the data in any aggregation within 24
   hours of the request, even before deletion completes.

This obligation flows from the applicable data-protection law (§10.1);
the spec encodes the wire-level facts required to prove
compliance.

## 10.4 Telemetry boundary

`/v1/upstream/telemetry` (chapter 5 §5.6) is the only endpoint where
no `tenant_pseudo_id` correlation across batches is permitted in
v1.0. Aggregated metrics derived from telemetry MUST NOT be joined
to upstream business data on the platform side.

## 10.5 Sample-size floor

The 30-row floor (§3.10) is the practical anti-re-identification
control. The threshold is conservative; real-world implementations
may choose to raise it for sensitive crop / region combinations
(e.g. cannabis where legal). Lowering below 30 requires an RFC.

## 10.6 Cryptographic agility

All cryptographic choices in v1.0 (HMAC-SHA256, JWT RS256, SHA-256
manifest hashes) are common in 2026 and have at least a decade of
deployment headroom. A future MAJOR may introduce a header-based
algorithm-negotiation mechanism if any of these primitives weaken.

Until then, conformant implementations MUST NOT silently downgrade.
Servers receiving a header with an unsupported algorithm MUST
reject `400 invalid_request`.

## 10.7 Subprocessors

Platforms that subprocess upstream data (e.g. forward credit packs
to a partner bank) MUST disclose this in their privacy policy and
the platform UI. The wire contract does not enforce this — it cannot
— but the audit-log discipline of §10.2 makes the forwarding
detectable from the client side: a credit-pack with
`recipient_id: BANK_X` that the owner did not list in their
Manifest's `recipients` would have failed `422
manifest_field_not_allowed`.

## 10.8 Conformance attestation

An implementer may publish a conformance attestation alongside their
CTS report. Suggested format (`SECURITY-and-COMPLIANCE.md` in the
implementer's repo):

```markdown
# Conformance attestation

- Project name:     X
- Spec version:     1.0.0
- Claimed level:    L2 Full
- CTS report:       https://.../cts-report.json
- Date:             2026-09-01
- Contact:          security@x.example
```

Attestations are not gated by the steward; they are public claims
that implementer competitors can verify.
