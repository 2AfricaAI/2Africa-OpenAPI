<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# Changelog

All notable changes to the 2Africa OpenAPI specification are recorded
here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versioning follows [SemVer 2.0.0](https://semver.org/).

The spec uses the **`Deprecation:`** and **`Sunset:`** HTTP headers to
signal upcoming removals; deprecations also appear in this log under a
`Deprecated` heading 12 months before removal.

---

## [Unreleased]

### Added
- Nothing yet.

### Changed
- Nothing yet.

### Deprecated
- Nothing yet.

### Removed
- Nothing yet.

### Fixed
- Nothing yet.

### Security
- Nothing yet.

---

## [0.1.0-skeleton] — 2026-05-29

Initial repository scaffold. **Not** a usable specification — this
release exists only to bootstrap the governance and lint
infrastructure.

### Added
- Repository skeleton: `spec/`, `docs/`, `sdks/{java,python,javascript}/`,
  `examples/`, `tests/`, `.github/workflows/`.
- Dual license:
  - `LICENSE-spec` — CC BY 4.0 (covers `spec/`, `docs/`)
  - `LICENSE-sdk`  — Apache-2.0 (covers `sdks/`, `examples/`, `tests/`)
  - `NOTICE` — dual-license summary and third-party standard references
- Governance documents:
  - `README.md` — what this is, what it is not, where to start
  - `GOVERNANCE.md` — RFC process, deprecation policy, Steering
    Committee charter (forming)
  - `CONTRIBUTING.md` — RFC workflow and style conventions
  - `CODE_OF_CONDUCT.md` — Contributor Covenant 2.1
  - `SECURITY.md` — coordinated disclosure policy
  - `CHANGELOG.md` — this file
- Placeholder specs (real content lands in Sprint 1):
  - `spec/openapi.yaml` — OpenAPI 3.1, only `GET /healthz` defined
  - `spec/privacy-manifest.schema.yaml` — JSON Schema placeholder
  - `spec/webhooks.asyncapi.yaml` — AsyncAPI 2.6 placeholder
- Lint config:
  - `.spectral.yml` — Spectral rules (extends `spectral:oas`,
    `spectral:asyncapi`, plus local rules for snake_case, kebab-case,
    UUID examples)
- CI workflows:
  - `.github/workflows/spec-lint.yml` — runs Spectral on every push & PR
  - `.github/workflows/markdown-lint.yml` — runs markdownlint
- `.gitignore` — excludes `*.docx` (internal PRD drafts must never be
  committed)

### Notes
- Local working directory on the maintainer machine is
  `C:\Claude Project\2Africa OpenAPI\` (with space). GitHub remote is
  `github.com/2AfricaAI/2Africa-OpenAPI` (with hyphen).
- The internal PRD drafts (`*.docx`) are not the standard. The standard
  lives in `spec/` and `docs/`. If they diverge, `spec/` and `docs/`
  win.

[Unreleased]: https://github.com/2AfricaAI/2Africa-OpenAPI/compare/v0.1.0-skeleton...HEAD
[0.1.0-skeleton]: https://github.com/2AfricaAI/2Africa-OpenAPI/releases/tag/v0.1.0-skeleton
