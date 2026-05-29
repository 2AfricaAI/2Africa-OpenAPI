<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Helpers (single-file, no packaging)

Tiny, zero-dependency utilities that implement the cryptographic and
canonical-form pieces of the spec. Each file is one drop-in unit — no
package install, no transitive dependencies.

Use them when:

- You're writing raw HTTP against `spec/openapi.yaml` without a full SDK.
- You want to vendor proven crypto into your project without taking an
  extra `pip`/`maven`/`npm` dependency.
- Your language isn't covered by the official SDKs (the patterns
  translate one-to-one to Go / Rust / PHP / Ruby).

## What's here

| Helper          | Purpose                                            | Spec section     |
| --------------- | -------------------------------------------------- | ---------------- |
| `pkce`          | Generate PKCE `code_verifier` + S256 `code_challenge` | §2.3              |
| `manifest_hash` | RFC 8785-aligned canonical SHA-256 of a Privacy Manifest | §4.3            |
| `webhook_verify` | HMAC-SHA256 webhook signature + replay-window check | §7.4             |
| `jwt_validate`  | Project-specific JWT claim rules (iss / aud / scope / leeway) | §2.5      |

All four are provided in **Python**, **Java**, and **JavaScript / TypeScript**.
Each is a single file, runnable as a self-test (`python3 pkce.py`,
`javac Pkce.java && java Pkce`, `node --experimental-strip-types pkce.ts`).

## Layout

```
helpers/
├── python/
│   ├── pkce.py
│   ├── manifest_hash.py
│   ├── webhook_verify.py
│   └── jwt_validate.py
├── java/
│   ├── Pkce.java
│   ├── ManifestHash.java
│   ├── WebhookVerify.java
│   └── JwtValidate.java
└── js/
    ├── pkce.ts
    ├── manifest-hash.ts
    ├── webhook-verify.ts
    └── jwt-validate.ts
```

## Vendor by `curl` (recommended)

```bash
mkdir -p src/vendor/twoafrica
curl -O https://raw.githubusercontent.com/2AfricaAI/2Africa-OpenAPI/main/examples/helpers/python/manifest_hash.py
mv manifest_hash.py src/vendor/twoafrica/
```

Or with `git subtree` / `git submodule` if you want the whole
`examples/helpers/` tree under your repo's control.

There is intentionally **no PyPI / Maven / npm package** for these — the
files are tiny enough to vendor, and avoiding a third-party dependency
is the whole point.

## Coverage

| Concern                        | Python | Java | JS/TS |
| ------------------------------ | :----: | :--: | :---: |
| OAuth PKCE generation          |   ✓    |  ✓   |   ✓   |
| Manifest canonical hash        |   ✓    |  ✓   |   ✓   |
| Webhook HMAC + replay verify   |   ✓    |  ✓   |   ✓   |
| JWT claim rules (no signature) |   ✓    |  ✓   |   ✓   |

JWT signature verification is **not** in these helpers — pair with the
ecosystem standard (`PyJWT`, Auth0 java-jwt, `jose`). The helpers only
encode the project-specific claim rules (`iss` / `aud` / `scope`).

## License

Apache-2.0. Copy, fork, adapt freely.
