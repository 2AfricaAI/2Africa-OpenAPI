<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Prism mock fixture

Start a Prism mock server from `spec/openapi.yaml` on `:4010` and point
the CTS at it. Useful for CI runs without a live sandbox.

```bash
./start-prism.sh                    # in one terminal
# in another:
export CTS_BASE_URL=http://localhost:4010
export CTS_ACCESS_TOKEN=anything    # Prism doesn't enforce auth
cd ../pytest
pytest -m l1                        # should pass against the mock
```

Note: Prism mocks return example payloads from `spec/openapi.yaml`. Some
spec-mandated semantics — manifest hash binding, sample-size floor,
idempotency replay — cannot be simulated by a pure mock. Those tests
will fail or skip against Prism and pass only against a real server.
