# Changelog

All notable changes to the public standards repository are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.8.0] - 2026-07-31

### Added

- `registry/tr-registry.yaml` — TR-SEC-013 (two-layer isolation for
  multi-agent tool and data access) and TR-TEST-007 (agent security-property
  claims verified against ground truth, not self-report), exported from the
  private-repo agent-platform deployment (private ADR-013, ADR-014).
  TR-SEC-013 graduates the "Compartmentalization worked example" item
  roadmapped since the 2026-07-13 Zero-Trust-for-AI-Agents review (private
  ADR-031), now backed by a running, hands-on-verified implementation rather
  than a design-only ADR; TR-TEST-007 is new content, motivated by two real
  false passes in the ADR-014 spike where an isolation/memory-scoping check
  "passed" only because the question was answered by the wrong backend, not
  the mechanism actually under test
- `examples/compartmentalized-agents/` — reference implementation:
  `ToolRegistry` (tool-registry scope) + `DataStore` (data-layer scope),
  with a test that deliberately misconfigures the tool layer and proves the
  data layer alone still blocks the resulting call (the defense-in-depth
  evidence, not just that both layers exist); `SelfReportingAgent`, with a
  test showing its self-report gives a false pass on a real isolation leak
  that `ToolRegistry.list_tools()` (ground truth) catches
- `docs/ai-engineering-operating-model.md` — "Rollout Sequencing" section
  (the layering rule: foundational infrastructure ships first, every later
  phase immediately usable on arrival), also graduated from the 2026-07-13
  review, second exemplar from private ADR-013's phased rollout table
- `templates/completion-checklist.md` — "Ground-truth verification for agent
  security claims" checklist item
- `AGENTS.md` — "Compartmentalized Multi-Agent Isolation" and "Ground-Truth
  Verification for Agent Security Claims" sections
- `docs/requirements-implementation-map.md` — rows for all three exports above
- `README.md` — `examples/compartmentalized-agents/` added to the worked-traces
  list and "Enforced workflow" section

Reviewed by a fresh-context reviewer agent before release: 0 blocking
findings, 2 advisory (the `README.md` gap above, and two added test cases
for previously-untested `DataStore`/`ToolRegistry` default-permission edge
cases) — both fixed prior to this release.

## [0.7.0] - 2026-07-26

### Added

- `registry/tr-registry.yaml` — TR-SEC-011 (content provenance tracked and
  trust derived fail-closed at retrieval), TR-SEC-012 (strict LLM
  output-schema validation — reject, never coerce), exported from the
  2026-07-13 Zero-Trust-for-AI-Agents review (private monorepo)
- `scripts/spotlighting-drift-guard.py` — single-sourced spotlighting
  constants (security notice + untrusted-content delimiters) enforcement:
  fails CI if any LLM boundary re-inlines a copy instead of importing the
  designated constants module
- `examples/spotlighting/` — worked example + planted re-inlined-copy
  fixture for the drift guard above (TR-SEC-005);
  `.github/workflows/spotlighting-drift-guard-demo.yml` proves the guard
  still catches it
- `examples/provenance-trust-tags/` — reference implementation of a
  fail-closed source-type → trust-level mapping with its own drift guard
  (every content type must be explicitly classified), and a quarantine
  helper routing untrusted/unverified content into the spotlighting layer
  (TR-SEC-011)
- `examples/strict-output-schema/` — before/after reference parser for LLM
  JSON output, with a live repro of the `bool("false") is True` fail-open
  coercion bug and the reject-never-coerce fix (TR-SEC-012)
- `AGENTS.md` — "Spotlighting at the Reasoning Boundary", "Memory /
  Provenance Hygiene", and "Strict LLM Output-Schema Validation" sections
- `docs/requirements-implementation-map.md` — rows for all three exports;
  the TR-SEC-005 row upgraded from "Documented" to "Documented + script +
  example"
- `ATTRIBUTIONS.md` — Microsoft public research on prompt-injection defenses
  (the "spotlighting" technique name and its measured effectiveness),
  cited via the same Anthropic eBook review

## [0.6.0] - 2026-07-20

### Added

- `README.md` — "Adopting this into your project" section: a six-step path
  (operating model → `AGENTS.md`/`agents/` → scripts against your own repo →
  templates → worked examples → `agent-skills-integration.md`) consolidating
  guidance that was previously scattered across the README and `docs/`

## [0.5.0] - 2026-07-16

### Added

- `registry/tr-registry.yaml` — TR-SEC-008 (local credential files
  permission-restricted and secret-scanned), TR-SEC-009 (CI pipelines run
  least-privilege and fully pinned), TR-SEC-010 (agent tool permission grants
  are a security boundary — least agency), exported from the private
  ATT&CK/ATLAS-informed security baseline (ADR-009)
- `templates/threat-model.md` — design-stage threat model mapping trust
  boundaries and data classification to MITRE ATT&CK/ATLAS techniques,
  required for ADRs introducing a new listener, credential, agent tool grant,
  or external content source; includes the "Impossible vs. Tedious" section
  (barrier vs. friction classification, from Anthropic's *Zero Trust for AI
  Agents*, ADR-010)
- `AGENTS.md` — "Threat Modeling and Least Agency" section presenting the
  impossible-vs-tedious test and TR-SEC-010 under the industry "least agency"
  name (OWASP), with citations
- `AGENTS.md` — "Guard Pattern: Co-located Reviewed Baselines" section
  documenting the "make dangerous changes loud, not impossible" governance
  pattern, including its honest limit
- `scripts/agent-permission-guard.py` — reference implementation of the
  co-located-baseline guard pattern for TR-SEC-010: hard-codes a reviewed set
  of agent tool-permission grants, fails on any forbidden wildcard
  write/install/exec/network grant, and fails on any grant absent from the
  baseline until a human adds it in the same PR. Exit-0/1/2 CLI contract
  matching the existing scripts; 7 tests in `tests/test_agent_permission_guard.py`
- `examples/agent-permission-guard/` — worked example: a settings file with a
  planted forbidden grant and a planted unreviewed grant, both caught by the
  guard; `.github/workflows/agent-permission-guard-demo.yml` gates this in CI
  the same way `config-drift-demo.yml` gates the config-drift worked example
- `examples/worked-example/docs/decisions/ADR-004-example.md` — synthetic ADR
  illustrating the security-baseline decision (public-safe rewrite of the
  private ADR-009 pattern)
- `scripts/llms-txt-generator.py` — generates `llms.txt` (v0.5 roadmap item) at repo
  root from the coding-relevant TR registry subset plus `agents/`, `templates/`, and
  `scripts/`, following the emerging llms.txt convention (https://llmstxt.org) so any
  agent framework that reads it — not only Cursor — can discover this repo's content.
  Generalizes `scripts/cursor-rules-adapter.py`'s "generate editor/agent context from
  the registry" pattern (`docs/agent-skills-integration.md` integration pattern 2):
  dynamically loads and reuses the Cursor adapter's registry parser and subset
  selection (`importlib`, since the adapter's filename is hyphenated and not
  import-able as a normal module) rather than re-implementing YAML parsing.
  `--check` drift-gates the committed `llms.txt` in `release-check.yml`, alongside
  the existing Cursor rules drift gate. 15 new tests
  (`tests/test_llms_txt_generator.py`), following the same subprocess-CLI testing
  pattern as `tests/test_cursor_rules_adapter.py`.

### Changed

- `.github/workflows/release-check.yml` and `.github/workflows/config-drift-demo.yml` —
  added an explicit least-privilege `permissions: contents: read` block and pinned
  `actions/checkout` and `actions/setup-python` to full commit SHAs (human-readable
  version in a trailing comment) to comply with the TR-SEC-009 this release exports;
  previously pinned to mutable version tags
- `ATTRIBUTIONS.md` — added rows for MITRE ATT&CK/ATLAS, Anthropic's *Zero Trust for
  AI Agents*, OWASP agentic security guidance, and `MadsLorentzen/ai-job-search`
  (comparative pattern reference for the guard script; no code copied)
- `docs/requirements-implementation-map.md` — rows for threat modeling, impossible-vs-tedious,
  least agency, the co-located guard pattern, and CI least-privilege/SHA pinning
- `README.md` — Quick start command for `agent-permission-guard.py`; Enforced workflow
  section links the new `examples/agent-permission-guard/` trace
- `ROADMAP.md` — generalized two private app names in the v0.6 section's prose
  (private-repo ADR citations) to `private-repo ADR-NNN`; the private repo's
  own leak-scan pattern only matched a trailing `/` and missed bare-word
  mentions, so this shipped in staging undetected until a dedicated review
  caught it before this tag was finalized. `docs/releasing.md` now requires
  running the private repo's leak scan as a mandatory pre-flight step
  (word-boundary matching fixed in the same change, private-repo only)

## [0.4.0] - 2026-07-10

### Added

- `AGENTS.md` — new "Behavioral Modes (TR-AGT-005)" section: a named,
  trigger-activated instruction set changing how an agent approaches a task,
  orthogonal to process-intensity gate strictness; each mode declares a trigger,
  activated behavior, exit condition, and precedence. `registry/tr-registry.yaml`
  gains the `TR-AGT-005` entry and `docs/requirements-implementation-map.md` a
  "Behavioral mode declaration" row. (Committed to the release source 2026-07-04,
  shortly after the v0.3.0 publish.)
- `scripts/cursor-rules-adapter.py` — Cursor rules adapter (v0.4 roadmap item 1):
  generates `.cursor/rules/*.mdc` project rules from the coding-relevant subset of
  `registry/tr-registry.yaml` (active requirements only, `TR-PUB-*` excluded;
  safety-critical sections `alwaysApply: true`, the rest description-attached).
  `--check` mode reports changed/missing/stale files so CI can gate the committed
  export. Stdlib-only with the same exit-0/1/2 contract as
  `check-config-consistency.py`; pinned by `tests/test_cursor_rules_adapter.py`.
- `examples/cursor-rules/` — pregenerated `.mdc` export of the current registry plus
  a usage README; `release-check` CI now runs the adapter in `--check` mode so this
  copy cannot drift from the registry.
- `docs/agent-skills-integration.md` — how this repo complements (not competes with)
  `agent-skills` collections (v0.4 roadmap item 2): skills are the task layer, the
  registry is the constraint layer; integration via TR-ID citations in skills,
  generated editor context (the Cursor adapter as the working example), and
  governance gates around skill output.
- `AGENTS.md` — new "Declarative Agent Profiles" section: unattended agent profiles are
  versioned YAML declarations (prompt, tools, routes, policy reference, trigger class,
  loop contracts) loaded by the runtime, never embedded in code — behavior changes become
  diffable PRs, and a profile survives re-hosting between a long-running host and an
  ephemeral CI job unchanged.
- `AGENTS.md` — new "Layered Policy Schema" section: three stacking policy levels
  (global / profile / run) in one versioned schema with two machine-checked invariants —
  a child level may only tighten its parent, and any cap change must keep the worst-case
  spend sum within the documented budget ceiling. Run-level budget is TR-AGT-003 field 4
  expressed as config. Both patterns originated in the maintainer's private platform
  design and were cross-validated against publicly documented agent-configuration and
  policy-stacking conventions.

### Changed

- `.github/workflows/release-check.yml` — unit-test step now runs the whole `tests/`
  directory (previously only `test_public_standards_release.py`, which silently
  skipped `test_check_config_consistency.py` in the public repo) and adds the
  Cursor-rules drift gate.
- `docs/releasing.md` — post-release checklist now requires verifying the published
  tree with a content-based diff; the v0.3.0 publish silently dropped a
  byte-size-neutral `ROADMAP.md` checkbox update because the sync compared only
  size and mtime.

### Fixed

- `scripts/check-config-consistency.py` — `SCAN_GLOBS` had two overlapping patterns
  (`config/*.yaml.example` and `config/*.example`) that both matched
  `search_config.yaml.example`, double-counting the file and duplicating its DRIFT
  location in output. Deduped `scan_files()` by path.
- `tests/test_check_config_consistency.py` — first unit test coverage for
  `check-config-consistency.py`; pins the exit-0/1/2 contract described in its own
  docstring and the SCAN_GLOBS dedup above.
- `.github/pull_request_template.md` — the "if example app touched" checklist item
  told contributors to run the checker with no args, which always exits 2 in this
  repo (no top-level app directories exist to discover); corrected to the invocation
  `config-drift-demo.yml` actually uses.

## [0.3.0] - 2026-07-04

### Added

- `examples/engine-interface/` — reference implementation of the TR-AGT-003 loop-contract
  pattern (SearXNG-inspired multi-source polling engine interface), plus a Loop Contracts
  pointer in `AGENTS.md` and a `requirements-implementation-map.md` row update. This was
  published directly to the public repo (commit `c20c72d`) without a corresponding private-repo
  change; pulled back into the private source here so the next `publish-public-standards.yml`
  run (which mirrors private → public via `rsync --delete`) does not silently delete it.
- `AGENTS.md` — new "MCP Tool Annotations (TR-AGT-003, field 5)" section: the
  `readOnlyHint`/`destructiveHint`/`idempotentHint`/`openWorldHint` convention for MCP-exposed
  nodes, ported from the private operating conventions (v0.3 roadmap item 1).
  `registry/tr-registry.yaml`'s `TR-AGT-003` entry extended to reference field 5.
- `examples/worked-example/` — the TR-AGT-004 trace now runs to completion: step 5 shows real
  `check-config-consistency.py` output (previously only described hypothetically) and a new
  step 6, `.github/workflows/config-drift-demo.yml`, is a CI job whose success condition is
  that the example's planted `local-gemma-model` drift is still detected — the "TR-ID → ADR →
  maturity row → script output → CI gate" full path the v0.3 roadmap asked for. Corrected the
  maturity-checklist's Annex A mapping in the process: the CI-gate evidence now lives on a new
  A.10 row (third-party/supplier relationships, matching the template's own mapping for
  `check-config-consistency.py`) instead of conflated into A.9 (human oversight); the now-closed
  `LUMIA-DEBT` tag was removed from `sample-app/CLAUDE.md`.
- `scripts/check-config-consistency.py` — new `--root PATH` flag (default: the script's own
  repo root), so it can scan any app monorepo, not just the one it lives in (P2). `README.md`'s
  usage example updated to show `--root /path/to/your/repo --app YourApp`.
- `registry/tr-registry.yaml` — `TR-PUB-006`: agent persona drift check between the private
  operating-persona tree and its public-standards rewrite. Compares last-changed time for each
  pair and fails on drift, forcing a human reconciliation decision instead of silent staleness.
- `.gitignore` — `__pycache__/`, `*.pyc`, `.pytest_cache/` (P3); nothing previously kept these
  out of a future `git add -A` in the public repo. Added to `docs/public-export-manifest.yaml`'s
  `generated:` list.

### Fixed

- `scripts/check-config-consistency.py` — an unknown `--app` name or a nonexistent `--root`
  previously printed a false "OK" (or crashed) instead of failing; now exits 2 with an
  explicit "Unknown app(s): ... . Known: ..." message (P1, P2).
- `ATTRIBUTIONS.md` — added the `detect-secrets` (Yelp, Apache-2.0) entry that should have
  shipped alongside v0.2.0's secret-scanning CI step but was missed.
- `ATTRIBUTIONS.md` — added a SearXNG (AGPL-3.0) entry for `examples/engine-interface/`'s
  cited pattern source, found during v0.3 release-readiness review; verified no code was
  copied (SearXNG's actual `searx/engines/demo_online.py` uses an unrelated module-level
  plugin API) before writing the entry.

### Changed

- `templates/completion-checklist.md` strengthened to match the private template's rigor:
  file:line evidence citation per acceptance criterion, an explicit anti-mock-masking clause
  on test completeness, and a "Reviewer scope complete" item (docs/ADRs, not just code, must
  be in a reviewer's stated scope). The public copy's own "Post-write verification" item is
  kept (P4) — nothing here required staying private.
- `.github/workflows/release-check.yml` — `actions/checkout`/`actions/setup-python` bumped to
  Node.js 24-compatible versions, clearing the Node 20 deprecation warning.

## [0.2.0] - 2026-06-26

### Added

- Secret-scanning step (`detect-secrets>=1.4,<2`) in `release-check` CI workflow; `^templates/`
  and `^examples/` path patterns excluded to avoid false positives on placeholder content (TR-PUB-002)
- `docs/releasing.md` — maintainer release process: export from source, local CI checks,
  CHANGELOG/ROADMAP updates, tagging, and version numbering convention
- `examples/worked-example/docs/decisions/ADR-002-example.md` — synthetic ADR illustrating
  the adoption of EARS syntax for testable requirements
- `examples/worked-example/docs/decisions/ADR-003-example.md` — synthetic ADR illustrating
  the four-field loop contract decision (TR-AGT-003)

## [0.1.0] - 2026-06-19

### Added

- Initial public standards toolkit: README, MIT `LICENSE`, `ATTRIBUTIONS.md`
- Curated `registry/tr-registry.yaml` (governance, agents, security, public-release TR-PUB-*)
- Public `AGENTS.md` with tool-neutral AI agent conventions
- Public agent role specs under `agents/`
- `docs/ai-engineering-operating-model.md`
- `docs/requirements-implementation-map.md`
- Templates: ADR, AI impact assessment, maturity checklist, governance review, LLM regression benchmark, LLM eval, completion checklist
- Scripts: `check-config-consistency.py`, `debt-report.py`, `public-export-check.py`
- Synthetic worked example under `examples/worked-example/`
- `CONTRIBUTING.md`, `SECURITY.md`, issue/PR templates, `release-check` CI workflow
- Roadmap and changelog for intentional release cadence

[Unreleased]: https://github.com/onesimplecode/ai-engineering-standards/compare/v0.8.0...HEAD
[0.8.0]: https://github.com/onesimplecode/ai-engineering-standards/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/onesimplecode/ai-engineering-standards/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/onesimplecode/ai-engineering-standards/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/onesimplecode/ai-engineering-standards/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/onesimplecode/ai-engineering-standards/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/onesimplecode/ai-engineering-standards/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/onesimplecode/ai-engineering-standards/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/onesimplecode/ai-engineering-standards/releases/tag/v0.1.0
