<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: Apache-2.0
-->

# @2africa/openapi · TypeScript SDK

[![npm](https://img.shields.io/npm/v/@2africa/openapi.svg)](https://www.npmjs.com/package/@2africa/openapi)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](../../LICENSE-sdk)

Hand-written, thin TypeScript client for the
[2Africa OpenAPI v1.0](https://github.com/2AfricaAI/2Africa-OpenAPI)
federation protocol. Works in Node 18+, browsers, Deno, Bun, Cloudflare
Workers — anywhere `fetch` exists.

```bash
npm install @2africa/openapi
```

## Quick start

```typescript
import { TwoAfricaClient } from "@2africa/openapi";
import { readFileSync } from "node:fs";
import { randomUUID } from "node:crypto";

const client = new TwoAfricaClient({
  baseUrl: "https://sandbox.agricloud.2africa.ai",
  accessToken: process.env.OPENAPI_TOKEN!,
});

// 1. publish a Privacy Manifest (PUT /v1/privacy-manifest)
const manifestYaml = readFileSync("../../examples/manifests/balanced.yaml", "utf-8");
await client.privacy.publishManifest(manifestYaml);
// manifestHash is now cached on the client.

// 2. submit yields
const ack = await client.upstream.yields({
  tenantPseudoId: "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  records: [{
    record_id: randomUUID(),
    crop_code: "TOMATO",
    region_code: "KE-30",
    harvest_date: "2026-05-20",
    quantity: { quantity: 1234.5, unit: "kg" },
  }],
});
console.log(`Accepted ${ack.accepted_count} records`);

// 3. read regional prices
const page = await client.downstream.prices({ regionCode: "KE-30", skuCode: "TOMATO_GRADE_A" });
for (const row of page.items) {
  console.log(`${row.region_code} ${row.sku_code} median ${row.median.amount} ${row.median.currency}`);
}
```

## Errors

```typescript
import { ManifestHashMismatch, RateLimited } from "@2africa/openapi";

try {
  await client.upstream.yields({ tenantPseudoId: "...", records: [...] });
} catch (e) {
  if (e instanceof ManifestHashMismatch) {
    // Re-publish the manifest and retry
  } else if (e instanceof RateLimited) {
    // Honour Retry-After
  } else {
    throw e;
  }
}
```

All non-2xx responses throw a subclass of `OpenApiError` with `.status`,
`.title`, `.type`, `.detail`, `.request_id`, and the raw RFC 7807 body.

## Helpers (zero-dep, optional)

If you only need PKCE / manifest hash / webhook signature / JWT claim
validation without the full SDK, vendor the single-file helpers from
the spec repo:

```bash
curl -O https://raw.githubusercontent.com/2AfricaAI/2Africa-OpenAPI/main/examples/helpers/js/manifest-hash.ts
```

## Development

```bash
npm install
npm test         # node --test, no jest / vitest needed
npm run build    # tsc → dist/
```

## License

Apache-2.0. See [LICENSE-sdk](../../LICENSE-sdk) at the repo root.
