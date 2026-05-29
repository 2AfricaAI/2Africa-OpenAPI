<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Compliance Test Suite (CTS)

> Status: skeleton. Sprint 1 will introduce a vendor-neutral CTS that
> any implementer can run against their server to prove conformance.
>
> Target stack:
>
> - **JUnit 5** runner (for JVM-based implementers)
> - **pytest** runner (for Python-based implementers)
> - **mock server** (Prism, generated from `spec/openapi.yaml`) for
>   client-side tests
> - Each level (L1, L2, L3) gets a separate tag so implementers can
>   declare and prove the level they target.

All test code is Apache-2.0.
