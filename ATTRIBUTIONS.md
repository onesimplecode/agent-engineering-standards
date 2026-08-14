# Attributions and Third-Party Influences

Agent Engineering Standards documents ideas and patterns learned from other
projects and standards. **No third-party code or substantial third-party prose is
included unless explicitly noted below.** Shipped templates, scripts, registry entries,
and examples are maintainer-authored unless a file header states otherwise.

## Open-source projects (ideas and selective adoption)

| Source | License | How used |
|--------|---------|----------|
| [Yelp/detect-secrets](https://github.com/Yelp/detect-secrets) | Apache-2.0 | Runtime CI dependency used in `release-check` workflow to scan the staging tree for accidental secrets before publish. Installed via pip; no code copied into this repository. |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | MIT | Process baseline evaluation; ADR lifecycle, CI quality-gate concepts, reviewer procedure patterns. Not a code fork. |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | MIT | Debt-tag convention, config consistency checking concept; adapted as `TECH-DEBT:` / `POC-EXCEPTION:` and `check-config-consistency.py`. |
| [MODSetter/SurfSense](https://github.com/MODSetter/SurfSense) | Apache-2.0 | Comparative analysis only; selective pattern adoption (RRF, automations) documented in private app ADRs — not shipped as SurfSense code. |
| Karpathy LLM Wiki (public write-ups) | N/A (ideas) | Three-layer vault structure, file-based session state, ingest queue patterns — described and reimplemented independently. |
| [SearXNG](https://github.com/searxng/searxng) | AGPL-3.0 | Comparative pattern reference only for `examples/engine-interface/` (TR-AGT-003 loop contract demo). No code copied — verified directly against `searx/engines/demo_online.py`, which uses a module-level `setup()`/`init()`/`request()`/`response()` plugin API, structurally unrelated to this example's synthetic ABC-based `source_name`/`fetch()`/`default_timeout` pattern. The per-engine declared-timeout *idea* is the only thing carried over. |
| [langchain-ai/openwiki](https://github.com/langchain-ai/openwiki) | MIT | Comparative pattern reference for deterministic vault post-processing (heal / index / link integrity) and a separate LLM-as-Judge structure critic (anti-anchoring inventory before scoring a draft). Patterns informed TR-AGT-006/007 and the reviewer "map independently" rule; no openwiki code copied. |
| [garrytan/gbrain](https://github.com/garrytan/gbrain) | (see upstream) | Comparative pattern reference for evidence-envelope fields, frozen additive-forever agent protocol versioning, and budgeted remediation. Informed ROADMAP frozen-protocol backlog item and Organizer MCP protocol shape; no gbrain code copied. Promote the frozen-protocol TR only after live-mount conformance exists in the private monorepo. |
| AGENTS.md ecosystem | Open standard | Complementary positioning; this repo focuses on governance/traceability, not replacing AGENTS.md. |
| [Microsoft Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit) | (see upstream) | Comparative positioning only; this repo focuses on design-time and repo-time standards, not runtime agent governance. |
| Dify and similar RAG/agent platforms | (varies by project) | Comparative positioning only; no code, docs, or implementation copied. |
| [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) | (see upstream) | Comparative pattern reference for `scripts/agent-permission-guard.py` (TR-SEC-010, v0.5): the idea of a script that hard-codes a reviewed baseline and fails CI on drift, popularized by that repo's `tools/security_guards.py` + `.github/workflows/ci.yml`. This repo's script is an independent implementation (JSON allowlist parsing, forbidden-pattern regexes, exit-0/1/2 CLI contract) — no code copied. Also cited for thin-pointer multi-runtime layout (ROADMAP v0.9) and for honest CI-limit header comments (`examples/honest-ci-limits/`). |
| [santifer/career-ops](https://github.com/santifer/career-ops) | MIT | Comparative pattern reference only (ROADMAP v0.9): thin-pointer multi-CLI `AGENTS.md` + `.agents/skills/`, third-party plugin skill output as untrusted under TR-SEC-005, and system/user path data-contract shape. No career-ops code or job-search modes copied. Adoption decision lives in the private monorepo. |
| [koala73/worldmonitor](https://github.com/koala73/worldmonitor) | AGPL-3.0 | Comparative pattern reference only: SSRF allowlist + redirect-hop re-check with honest residuals informed `examples/ssrf-allowlist/` (MIT reimplementation — no upstream code); remaining ROADMAP backlog items (graded source confidence, hybrid classify-with-source, LLM call dedup) stay citation-only until privately dogfooded. Adoption decision lives in the private monorepo (ADR-017). |

## Ideas and vocabulary (not software)

| Source | How used |
|--------|----------|
| MITRE ATT&CK (https://attack.mitre.org/) and MITRE ATLAS (https://atlas.mitre.org/) | Public technique catalogs cited by TR-ID and by name in `registry/tr-registry.yaml` and `templates/threat-model.md` to give threat-model findings a shared, falsifiable vocabulary. No content reproduced beyond technique IDs and short names. |
| Anthropic, "Zero Trust for AI Agents" (2026) | Source of the "impossible vs. tedious" design test (`templates/threat-model.md`, `AGENTS.md`) — the barrier-vs-friction classification of a mitigation's real strength. Concept adopted and reworded; no text reproduced. |
| OWASP agentic application security guidance | Source of the "least agency" framing applied to TR-SEC-010 (`AGENTS.md`) — least privilege extended to what an agent tool can do, how often, and where. Concept and term adopted; no text reproduced. |
| Microsoft public research on prompt-injection defenses | Source of the "spotlighting" technique name and its measured effectiveness (indirect prompt-injection success reduced from >50% to <2%), cited in `AGENTS.md`, `scripts/spotlighting-drift-guard.py`, and `examples/spotlighting/README.md` (TR-SEC-005) via Anthropic's *Zero Trust for AI Agents* eBook, which references the same figure. Technique name and effect-size figure cited; no text reproduced. |

## Standards (document shapes, not certification)

| Source | How used |
|--------|----------|
| ISO/IEC 42001:2023 | Maturity checklist and impact assessment **templates** inspired by Annex A control objectives. No claim of ISO certification. |
| [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) | Changelog structure and headings only. |

## Maintainer-authored content

Templates, TR registry entries, scripts, worked examples, and ADRs in this repository are
authored by David Lin unless a file header states otherwise. The MIT
license text in `LICENSE` is the standard MIT License text with project-specific
copyright attribution.

## Adding third-party content

Before merging third-party code or substantial prose:

1. Confirm license compatibility with MIT.
2. Add a row to this file: source URL, license, copied vs adapted, affected paths.
3. Complete the maintainer legal/open-source review before publishing.
