<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: Apache-2.0
-->

# CTS · JUnit 5 runner

JVM-friendly counterpart to the pytest runner. Uses only JDK 17 stdlib
(`java.net.http.HttpClient`) — no OkHttp, no Spring, no Jackson; the
goal is portability across implementer build setups.

```bash
mvn -Dtest.base.url=https://your-server.example \
    -Dtest.access.token=<JWT> \
    -Dgroups=l1 test
```

Tags map 1:1 with the pytest markers: `l1` / `l2` / `l3`.
