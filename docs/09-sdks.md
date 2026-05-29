<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# 9 · SDKs

The specification is implementer-agnostic; anyone can generate an
SDK from `spec/openapi.yaml`. The repository ships reference SDKs
in three languages:

| Language        | Package                    | Source                                       |
| --------------- | -------------------------- | -------------------------------------------- |
| Java            | `ai.toafrica:openapi-sdk`  | [`sdks/java/`](../sdks/java/) (Sprint 2)     |
| Python          | `twoafrica-openapi`        | [`sdks/python/`](../sdks/python/) (Sprint 2) |
| JavaScript / TS | `@2africa/openapi`         | [`sdks/javascript/`](../sdks/javascript/) (Sprint 2) |

All three are **Apache-2.0**, intentionally a different licence from
the spec itself (CC BY 4.0). Apache-2.0 is the most frictionless
licence for both open-source and proprietary downstreams.

## 9.1 Generation pipeline

Each SDK is generated from `spec/openapi.yaml` via
[OpenAPI Generator](https://openapi-generator.tech) and then hand-
polished. The generator templates live alongside each SDK
(`sdks/<lang>/openapi-generator-templates/`). Regeneration is
automated by `make sdk` (Sprint 2).

A third party regenerating the SDK MUST keep the package name out
of the `ai.toafrica` / `twoafrica-openapi` / `@2africa` namespaces
(those are reserved for the reference SDKs). The spec licence does
not grant trademark.

## 9.2 Conformance test suite (CTS)

The CTS lives in [`tests/`](../tests) (Sprint 2). It is a vendor-
neutral test runner any implementer can point at their server to
prove conformance:

- **JUnit 5** runner for JVM-based implementers.
- **pytest** runner for Python-based implementers.
- A **mock server** (Prism, generated from `spec/openapi.yaml`) for
  client-side conformance tests.

Each level (L1, L2, L3) is a JUnit/pytest tag. An implementer claims
a level by passing the test set with that tag and posting the
resulting report.

## 9.3 Java SDK quick start (Sprint 2 preview)

```java
import ai.toafrica.openapi.ApiClient;
import ai.toafrica.openapi.api.UpstreamApi;
import ai.toafrica.openapi.model.YieldRecord;

ApiClient client = new ApiClient()
    .setBasePath("https://sandbox.agricloud.2africa.ai")
    .setAccessToken(token);

UpstreamApi api = new UpstreamApi(client);
api.postUpstreamYields(
    "1.0.0-rc1",            // X-Spec-Version
    manifestHash,            // X-Privacy-Manifest-Hash
    UUID.randomUUID(),       // Idempotency-Key
    request                  // YieldsRequest
);
```

## 9.4 Python SDK quick start (Sprint 2 preview)

```python
from twoafrica_openapi import ApiClient, Configuration, UpstreamApi
from twoafrica_openapi.models import YieldRecord, Quantity

cfg = Configuration(host="https://sandbox.agricloud.2africa.ai")
cfg.access_token = token

api = UpstreamApi(ApiClient(cfg))
api.post_upstream_yields(
    x_spec_version="1.0.0-rc1",
    x_privacy_manifest_hash=manifest_hash,
    idempotency_key=str(uuid4()),
    body=request,
)
```

## 9.5 JavaScript SDK quick start (Sprint 2 preview)

```typescript
import { ApiClient, UpstreamApi } from "@2africa/openapi";

const client = new ApiClient({
  basePath: "https://sandbox.agricloud.2africa.ai",
  accessToken: token,
});

const api = new UpstreamApi(client);
await api.postUpstreamYields({
  xSpecVersion: "1.0.0-rc1",
  xPrivacyManifestHash: manifestHash,
  idempotencyKey: crypto.randomUUID(),
  body: request,
});
```

## 9.6 Generating your own SDK

The spec is OpenAPI 3.1, fully self-contained, no vendor extensions
the public OpenAPI Generator can't parse. To generate a Go SDK, for
example:

```bash
openapi-generator-cli generate \
  -i spec/openapi.yaml \
  -g go \
  -o my-go-sdk
```

Any conformance issues introduced by the generator (e.g. missing
header support, wrong content-type handling) are out of scope for
this repository; please file them with the generator project.

## 9.7 Webhook SDKs

Webhook handling is intentionally NOT inside the language-SDK
namespaces because it lives in the receiver application (a Spring
controller, a Flask view, an Express handler). The reference
verifier in `examples/webhook-replay/verify_signature.py` (Python)
is ~80 lines and easy to translate.

Sprint 2 will add `sdks/<lang>/webhook/` helper modules wrapping the
HMAC verification pattern for the three reference languages.
