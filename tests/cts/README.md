<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Compliance Test Suite (CTS)

A vendor-neutral test runner that exercises any conformant server
against the v1.0 spec. Implementers run it to claim a conformance level
([L1 Basic / L2 Full / L3 Advanced](../../docs/01-versioning.md#13-conformance-levels))
and publish the report alongside their implementation.

```
tests/cts/
├── pytest/             ← pytest runner (Python 3.10+, fast, no JVM)
├── junit/              ← JUnit 5 runner (JVM implementers)
└── mock/               ← Prism mock-server fixture for offline CTS runs
```

Both runners are tagged by level — pick the level you target.

## Quick start (pytest)

```bash
pip install pytest requests pyyaml
export CTS_BASE_URL="https://your-server.example"
export CTS_ACCESS_TOKEN="<JWT>"
export CTS_MANIFEST_PATH="../../examples/manifests/balanced.yaml"

cd tests/cts/pytest

# Run only the L1 Basic tier
pytest -m l1 -v

# Full L2 conformance
pytest -m "l1 or l2" -v --junit-xml=cts-l2-report.xml
```

## Quick start (JUnit 5)

```bash
cd tests/cts/junit
mvn -Dtest.base.url=https://your-server.example \
    -Dtest.access.token=<JWT> \
    -Dgroups=l1 test
```

## Offline mode (Prism mock)

If you do not yet have a live server but want to validate that the
CTS itself runs against the spec, point it at the bundled Prism mock:

```bash
cd tests/cts/mock
./start-prism.sh         # docker-based Prism on :4010
export CTS_BASE_URL=http://localhost:4010
cd ../pytest
pytest -m l1            # passes against the mock — proves test plumbing OK
```

## Level coverage

| Test class           | L1 | L2 | L3 |
| -------------------- | :-: | :-: | :-: |
| OAuth metadata       | ✓   | ✓   | ✓   |
| PKCE round-trip      | ✓   | ✓   | ✓   |
| Privacy Manifest hash binding | ✓ | ✓ | ✓ |
| 1 upstream endpoint (yields)  | ✓ | ✓ | ✓ |
| All 5 upstream endpoints      |   | ✓ | ✓ |
| All 5 downstream endpoints    |   | ✓ | ✓ |
| Webhook signature verification|   | ✓ | ✓ |
| RFC 7807 error catalogue      |   | ✓ | ✓ |
| Field-level encryption        |   |   | ✓ |
| Federated identity            |   |   | ✓ |

## Reporting conformance

After a green run, generate a report:

```bash
pytest -m "l1 or l2" --junit-xml=cts-l2-report.xml --html=cts-l2-report.html
```

Upload the XML/HTML to a public URL and link it from your repo's
`SECURITY-AND-COMPLIANCE.md` per [governance §4](../../GOVERNANCE.md#4--implementer-registry).
