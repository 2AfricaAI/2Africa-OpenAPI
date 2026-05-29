<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# 4 · Privacy Manifest

## 4.1 Goal

The Privacy Manifest is a YAML document that the data owner publishes
to declare, per upstream endpoint, *exactly* which fields the client
is permitted to send. The platform stores only the SHA-256 hash of
the canonicalised manifest and enforces it on every upstream call.

Goals:

1. **Owner-controlled.** Each tenant authors and signs their own.
2. **Cryptographically attested.** Server rejects any upstream request
   whose manifest hash doesn't match.
3. **Auditable.** Hash + owner_id + generated_at appear in every
   server-side audit log entry.
4. **Default OFF.** Absent or unpublished manifest = no upstream
   data permitted.

The full JSON-Schema 2020-12 contract lives in
[`spec/privacy-manifest.schema.yaml`](../spec/privacy-manifest.schema.yaml).

## 4.2 Document shape

Top-level required fields:

| Field             | Type   | Notes                                       |
| ----------------- | ------ | ------------------------------------------- |
| `manifest_version`| string | SemVer of the manifest format. v1.0 = `1.0.0`. |
| `profile`         | enum   | `strict` / `balanced` / `open` / `custom`.  |
| `generated_at`    | string | ISO 8601 UTC. Server logs this.             |
| `owner_id`        | string | Stable id of the human or role that authored. |
| `endpoints`       | object | Per-endpoint policies. Absence = OFF.       |

Optional:

- `notes` — free-form text up to 2 000 chars the owner attaches.

### 4.2.1 `endpoints.<name>` (EndpointPolicy)

| Field                  | Type    | Default       | Notes                                  |
| ---------------------- | ------- | ------------- | -------------------------------------- |
| `enabled`              | boolean | (required)    | Master switch.                         |
| `allow_fields`         | array   | required-only | Dotted field paths the client may send. |
| `deny_fields`          | array   | none          | Overlaid deny on top of `allow_fields`. |
| `region_floor`         | enum    | `subdivision` | `country` or `subdivision` (no finer). |
| `retention_days`       | integer | impl-default  | Max server retention. `0` = no retention. |
| `rate_limit_per_hour`  | integer | impl-default  | Owner-imposed ceiling.                  |
| `recipients`           | array   | empty         | credit-pack only: bank allow-list.      |

## 4.3 Hash binding

Every upstream request MUST present the canonical hash in:

```http
X-Privacy-Manifest-Hash: sha256:a4f8b9c2d6e1f3a7b5d8c2e6f9a1b4d7e2c5f8a1b4d7e2c5f8a1b4d7e2c5f8a1
```

Servers MUST:

1. Look up the manifest hash currently cached for `client_id`.
2. Compare with the request header.
3. If they differ, reject with `422 manifest_hash_mismatch` and a
   Problem `detail` instructing the client to PUT the latest
   manifest.
4. If they match, validate the request body: every field in the body
   MUST appear in the endpoint's effective allow-list (allow minus
   deny). A field outside that list returns
   `422 manifest_field_not_allowed`.

### 4.3.1 Canonical hash algorithm

To make hashes reproducible across YAML parsers:

1. Parse the YAML into the JSON Schema's data model.
2. Re-serialise as **JSON**, with object keys sorted lexicographically
   at every level (RFC 8785 JCS).
3. Encode as UTF-8.
4. `sha256` of the resulting bytes.
5. Prefix the hex digest with `sha256:`.

Reference implementations of step 1-4 are in each SDK
(`sdks/*/privacy/canonical_hash.*`).

## 4.4 Publication

Clients publish the manifest with:

```http
PUT /v1/privacy-manifest HTTP/1.1
Host: api.agricloud.2africa.ai
Authorization: Bearer <jwt with scope privacy:manage>
Content-Type: application/yaml
X-Spec-Version: 1.0.0-rc1
Idempotency-Key: 3f55cd84-3a3a-46f3-9b1a-9e16f8b86e2a

manifest_version: 1.0.0
profile: balanced
generated_at: '2026-05-29T14:30:00Z'
owner_id: jane.doe@example-farm.ke
endpoints:
  yields:
    enabled: true
    region_floor: subdivision
    retention_days: 365
    rate_limit_per_hour: 100
  # ... etc
```

Response:

```json
{
  "manifest_hash": "sha256:a4f8b9...",
  "accepted_at":   "2026-05-29T14:30:01Z"
}
```

The client persists the returned hash locally and includes it in the
`X-Privacy-Manifest-Hash` header on subsequent upstream calls until
the next PUT.

## 4.5 Preset profiles

Three presets ship in [`examples/manifests/`](../examples/manifests):

| Preset     | Yields | Prices | GAP | Credit-pack | Telemetry |
| ---------- | :----: | :----: | :-: | :---------: | :-------: |
| `strict`   |   ✗    |   ✗    |  ✗  |      ✗      |     ✓     |
| `balanced` |   ✓    |   ✓    |  ✓  |      ✗      |     ✓     |
| `open`     |   ✓    |   ✓    |  ✓  |      ✓      |     ✓     |
| `custom`   | author's choice — `profile: custom` is purely informational |

New tenants ship `strict` by default. UI tooling MUST require an
explicit user gesture to move to `balanced` or `open`.

## 4.6 Manifest lifecycle

1. **Draft.** Authored locally, not yet published.
2. **Published.** PUT succeeded; server cached its hash; client uses
   it on every upstream call.
3. **Stale.** Owner edited the local copy but has not republished.
   Client SHOULD refuse to make any upstream call in this state —
   it would fail with `manifest_hash_mismatch`.
4. **Superseded.** A newer manifest has been published. The old one
   is no longer enforceable.

Servers keep an audit history of published manifest hashes for the
duration of the longest `retention_days` in the most recent
manifest, plus 90 days.

## 4.7 Why an allow-list, not a deny-list

Allow-listing is fail-safe: a new field added to an endpoint's
schema (a MINOR release) does **not** start leaking until the owner
explicitly includes it. A deny-list would silently leak on every
MINOR.

The `deny_fields` list exists only as a refinement when a tenant
allow-lists a parent object and wants to subtract a single nested
field.

## 4.8 What a manifest does NOT control

The Privacy Manifest controls upstream payload **content**. It does
not control:

- Authentication. (Handle with token revocation; chapter 2.)
- Downstream reads. (Those are platform-side filtering; chapter 6.)
- Webhook subscriptions. (Those are configured separately.)

A tenant who wants to leave the federation entirely revokes all
tokens (see chapter 2 §2.7); the manifest then becomes inert.
