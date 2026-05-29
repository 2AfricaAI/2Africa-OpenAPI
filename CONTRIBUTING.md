<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# Contributing to 2Africa OpenAPI

Thank you for considering contributing. The standard belongs to its
implementers — your input shapes it.

This file covers the *mechanics*. The *substance* of how decisions are
made lives in [GOVERNANCE.md](./GOVERNANCE.md).

---

## Quick decision tree

| What you want to do                            | How                                                                              |
| ---------------------------------------------- | -------------------------------------------------------------------------------- |
| Fix a typo / dead link / wording               | Open a PR directly. One maintainer review + green CI = merge.                    |
| Suggest a new field / endpoint / behaviour     | Open an **RFC** (see below) — required, no shortcuts.                            |
| Report a bug in the spec (it contradicts itself or omits a behaviour) | Open an issue first; we'll triage. Likely → RFC. |
| Report a security issue                        | **Do NOT** open a public issue. Email `security@2africa.ai`. See [SECURITY.md](./SECURITY.md). |
| Add yourself to the implementer registry       | PR to `docs/implementers.md` (Sprint 1+).                                        |
| Improve an SDK                                 | PR to the relevant `sdks/<lang>/` tree. SDKs are Apache-2.0; CLA-equivalent applies. |

---

## 1 · Setting up locally

```bash
git clone https://github.com/2AfricaAI/2Africa-OpenAPI.git
cd 2Africa-OpenAPI

# Lint the spec
npm install -g @stoplight/spectral-cli
spectral lint spec/openapi.yaml

# Lint markdown
npm install -g markdownlint-cli
markdownlint "**/*.md" --ignore node_modules
```

CI runs the same commands. If they pass locally, they will pass on PR.

---

## 2 · The RFC process

Substantive changes — anything that changes wire behaviour or adds
surface area — require an RFC. See
[GOVERNANCE.md §2.2](./GOVERNANCE.md#22-substantive-changes--rfc-process).

### Workflow

1. **Fork & branch.** Branch name: `rfc/NNN-short-title` where `NNN` is
   the next free 3-digit number (look in `rfcs/`).
2. **Create the RFC file** at `rfcs/NNN-short-title.md` using the
   template at `rfcs/0000-template.md` (added Sprint 1).
3. **Open a PR** labelled `rfc:open`. The 14-day comment window starts.
4. **Engage** — respond to comments, iterate.
5. **Acceptance criteria** are listed in GOVERNANCE.md §2.2.
6. On acceptance: the RFC PR is merged, *then* a separate spec PR
   implements the change and adds a CHANGELOG entry.

### What a good RFC looks like

- **Problem** — what real implementer pain motivates this?
- **Proposal** — concrete wire change, with example JSON.
- **Alternatives considered** — at least two.
- **Backwards compatibility** — MINOR or MAJOR? deprecation plan?
- **Reference implementer commitment** — who will implement first?
- **Open questions** — explicit list.

---

## 3 · Commit & PR style

- Commits in English, imperative mood:
  `add credit-pack endpoint`, not `Added credit-pack endpoint`.
- One conceptual change per PR. Spec change and CHANGELOG entry go
  together; SDK regeneration is a separate PR.
- Reference the RFC: `closes RFC-014`.
- Sign off your commits (`git commit -s`) — this confirms you have
  authority to contribute the work under the appropriate license
  (CC BY 4.0 for spec/docs, Apache-2.0 for code).

---

## 4 · Style conventions

| Area                       | Convention                                         |
| -------------------------- | -------------------------------------------------- |
| JSON field names           | `snake_case`                                       |
| URL paths                  | `kebab-case` (e.g. `/v1/upstream/credit-pack`)     |
| Constants                  | `SCREAMING_SNAKE_CASE` (e.g. `TOMATO`)             |
| YAML files                 | 2-space indent, no tabs, trailing newline          |
| Markdown                   | Wrap at 80 cols where reasonable; tables OK longer |
| English                    | International English (programme, organisation)    |
| Date format in prose       | ISO 8601 (`2026-05-29`)                            |

`spectral lint` enforces most of the YAML rules; `markdownlint`
enforces the prose rules.

---

## 5 · Two licenses, one repo

When you contribute to a file under `spec/` or `docs/`, your
contribution is licensed under **CC BY 4.0**. When you contribute to a
file under `sdks/`, `examples/`, or `tests/`, your contribution is
licensed under **Apache-2.0**. By opening a PR you affirm you have
authority to do so.

There is no separate CLA. The signed-off-by line on each commit is the
contribution attestation.

---

## 6 · Code of conduct

All interaction in this repository — issues, PRs, RFC discussions — is
governed by [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md).

---

## 7 · Where to start if you've never contributed to a standards repo

- Read the README and one chapter under `docs/` end-to-end.
- Find a "good first issue" label.
- Watch the issue tracker for two weeks to see the *tone* of debate.
- For your first PR, pick something small and editorial. Get familiar
  with the review loop before proposing a wire change.

Welcome.
