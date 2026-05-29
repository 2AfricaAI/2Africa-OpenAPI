<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Examples

Apache-2.0. Copy and adapt freely.

## What's here

```
examples/
├── postman-collection.json          Postman v2.1, 11 requests
├── curl/                            One shell script per endpoint
│   ├── 01-healthz.sh
│   ├── 02-publish-manifest.sh
│   ├── 03-upstream-yields.sh
│   ├── 04-upstream-prices.sh
│   ├── 05-upstream-gap-records.sh
│   ├── 06-upstream-credit-pack.sh
│   ├── 07-upstream-telemetry.sh
│   ├── 08-downstream-dictionaries.sh
│   ├── 09-downstream-prices.sh
│   ├── 10-downstream-benchmarks.sh
│   ├── 11-downstream-marketplace.sh
│   └── 12-downstream-procurement.sh
├── manifests/                       Sample Privacy Manifests
│   ├── strict.yaml
│   ├── balanced.yaml                ← recommended default
│   └── open.yaml
├── helpers/                         ← Single-file zero-dep utilities (Sprint 2)
│   ├── python/  · pkce.py · manifest_hash.py · webhook_verify.py · jwt_validate.py
│   ├── java/    · Pkce.java · ManifestHash.java · WebhookVerify.java · JwtValidate.java
│   └── js/      · pkce.ts · manifest-hash.ts · webhook-verify.ts · jwt-validate.ts
└── webhook-replay/                  ← DEPRECATED, see helpers/python/webhook_verify.py
    └── verify_signature.py
```

See [`helpers/README.md`](./helpers/README.md) for the helper coverage matrix
and `curl` vendor instructions.

## Running the curl examples

Every script reads three environment variables:

```bash
export OPENAPI_HOST=https://sandbox.agricloud.2africa.ai
export OPENAPI_TOKEN=<JWT from /oauth/token>
export MANIFEST_HASH=sha256:<hash of your active Privacy Manifest>

./curl/01-healthz.sh
./curl/02-publish-manifest.sh ./manifests/balanced.yaml
./curl/03-upstream-yields.sh
```

The `MANIFEST_HASH` value is what `helpers/python/manifest_hash.py` (or its
Java / JS sibling) produces from your manifest file.

## Loading the Postman Collection

1. Import `postman-collection.json` into Postman.
2. Set the three collection variables (`base_url`, `access_token`,
   `manifest_hash`) at the top of the collection or in an environment.
3. Use the requests under **System / Upstream / Downstream** folders.

## Verifying a webhook signature

```bash
python3 helpers/python/webhook_verify.py    # self-test
```

Or in your own server, import `verify_signature` and call it with the
raw bytes of the request body (before any JSON parsing) and the
`X-AgriCloud-Signature` header. The same helper exists in Java
(`helpers/java/WebhookVerify.java`) and TypeScript
(`helpers/js/webhook-verify.ts`).
