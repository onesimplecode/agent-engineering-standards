# Roadmap

Releases are **curated and periodic**, not continuous dumps of unrelated work.
See `CHANGELOG.md` for shipped versions.

## v0.1 — Public standards baseline

- [x] Curated TR registry subset
- [x] Governance templates (ADR, impact assessment, maturity checklist, governance review)
- [x] Reference scripts: config consistency, debt report, public export check
- [x] Synthetic worked example
- [x] Contribution, security, and issue boundaries
- [x] Public `AGENTS.md`, role specs, operating model, and requirements map
- [x] Public LLM eval and completion/self-critique templates
- [x] Unit tests for `public-export-check.py` in CI

## v0.2 — Release hardening

- [x] Add a generic secret-scanning step to the `release-check` CI workflow
- [x] Document the maintainer release process
- [x] Public-safe process ADR examples explaining the governance decisions

## v0.3 — Enforced workflow example

- [x] Export MCP tool annotation conventions (TR-AGT-003 field 5) to public `AGENTS.md`
- [x] Worked example shows full path: TR-ID → ADR → maturity row → script output → CI gate
- [x] Sample GitHub Actions job that fails on config drift

## v0.4 — Cross-tool adapters

- [x] Cursor rules adapter generated from TR registry subset
- [x] Document integration with `agent-skills` (complement, not compete)

## v0.5 — CI-enforced security guardrails

- [x] Export the ATT&CK/ATLAS-informed security baseline (private ADR-009) to the
      public TR registry subset: TR-SEC-008 (local credential files
      permission-restricted and secret-scanned), TR-SEC-009 (CI pipelines run
      least-privilege and fully pinned — explicit `permissions:` block,
      SHA-pinned actions, exact dependency pins past POC tier), TR-SEC-010
      (agent tool permission grants are a security boundary — no wildcard
      write/install/network grants in agent allowlists). `release-check.yml`
      and `config-drift-demo.yml` brought into TR-SEC-009 compliance
      (explicit `permissions:` block, SHA-pinned actions) in the same change.
- [x] Export `templates/threat-model.md` — design-stage threat model mapping a
      change's trust boundaries and data classification to MITRE ATT&CK /
      ATLAS techniques; required for ADRs introducing a new listener,
      credential, agent tool grant, or external content source
- [x] Export the **"impossible vs. tedious" design test** (private ADR-010,
      from Anthropic's *Zero Trust for AI Agents*, 2026): every threat-model
      mitigation is classified as *barrier* (removes the capability) or
      *friction* (raises cost only, with its real backstop named) — friction-only
      controls degrade against agentic attackers with unlimited patience and
      near-zero per-attempt cost. Ships as a section of the threat-model
      template export above
- [x] Present the TR-SEC-010 export under its industry name — **least agency**
      (OWASP's extension of least privilege to agentic applications: constrain
      what each tool grant can do — how often and where included — not just
      what the identity can access). TR-SEC-010's own text covers the per-grant
      capability restriction; cite OWASP's agentic security guidance and
      Anthropic's Zero Trust eBook so the standard speaks the emerging shared
      vocabulary (private ADR-010)
- [x] Public-safe process ADR example explaining the baseline (why toolchain
      security — CI supply chain and agent permissions — is the attack surface
      of an agent-operated shop, per private ADR-009):
      `examples/worked-example/docs/decisions/ADR-004-example.md`
- [x] "Make dangerous changes loud, not impossible" guard pattern: a script that
      hard-codes the reviewed baseline (permissions allowlist) and fails CI on
      any drift, forcing the widening diff and the allowlist update into the
      same PR: `scripts/agent-permission-guard.py`, demoed against a planted
      forbidden + unreviewed grant in `examples/agent-permission-guard/` and
      gated in CI by `.github/workflows/agent-permission-guard-demo.yml`
      (original implementation of the pattern popularized by
      `MadsLorentzen/ai-job-search`'s `tools/security_guards.py`, not a copy)
- [x] Document as a public governance pattern: co-locate the guard with its own
      allowlist (not a separate config file), state the honest limit inline
      (a PR can edit the workflow itself — this catches accidents/casual
      attempts, not a determined author; branch protection + human review of
      workflow/settings diffs remain the real backstop):
      AGENTS.md "Guard Pattern: Co-located Reviewed Baselines"
- [x] `llms.txt` cross-tool discovery manifest generated from the TR registry,
      agent role specs, templates, and scripts (`scripts/llms-txt-generator.py`,
      drift-gated in CI) — generalizes the Cursor rules adapter pattern
      (v0.4 item 1) to any agent framework that reads the emerging llms.txt
      convention (https://llmstxt.org), not just Cursor

## v0.6 — Adoption guide

- [x] `README.md` "Adopting this into your project" section: a six-step path
      (operating-model doc, `AGENTS.md`/`agents/`, running the Quick-start
      scripts against the reader's own repo, `templates/`, the two worked
      examples, `docs/agent-skills-integration.md`) consolidating onboarding
      guidance that was previously scattered across the README and `docs/`

## v0.7 — Agentic security & operations patterns (current)

From the 2026-07-13 Zero-Trust-for-AI-Agents review (private ADRs: private-repo
ADR-030/031/032, private-repo ADR-018, and a private-repo deployment proposal). Two
maturity classes — this repo exports packaged practice, not aspirations.

**Export-ready (shipped + tested in the private monorepo, 2026-07-13):**

- [x] **Spotlighting at the reasoning boundary** (private ADR-030,
      private ADR-018): untrusted retrieved/external content is wrapped in
      explicit delimiters and every LLM call that sees it carries a firewall
      system message; the delimiter/notice strings are **single-sourced
      constants with a CI drift-guard test** that fails on any re-inlined copy
      — the drift guard is the enforceable artifact this repo ships
      (`scripts/spotlighting-drift-guard.py`, `examples/spotlighting/`)
- [x] **Memory/provenance hygiene** — new TR-SEC entry (the registry's gap
      against agentic memory-poisoning): source-tag content at ingest, derive
      trust via a **fail-closed** mapping at read time (unknown → untrusted;
      missing → unverified), validate provenance at *retrieval* not only at
      storage, and treat unverified/external content as quarantined data,
      never instructions (private ADR-030's implementation is the reference)
      (TR-SEC-011, `examples/provenance-trust-tags/`)
- [x] **Strict LLM output-schema validation** pattern + worked example: type
      AND range checks on every model-returned field, reject — never coerce —
      wrong types (canonical bug: Python `bool("false") is True` failing open
      through a relevance gate; private ADR-018); pairs with the existing
      single-source-of-truth convention
      (TR-SEC-012, `examples/strict-output-schema/`)

**Roadmapped — export after the private implementation proves them
(design-stage as of 2026-07-13; promotion to export requires the same
evidence TR-SEC-010 had — commits, tests, an operating track record):**

- [ ] **Disposition contract** — triage agents emit a structured disposition
      (query / think / report) as a loop-contract output field, extending
      TR-AGT-003 (private-repo deployment proposal)
- [ ] **Agreement-rate-gated authority promotion** — the measurable form of
      the advisory-first trust ramp: agent verdicts run advisory while
      human-agreement rate is measured; promotion to blocking/trusted cites
      the rate, rule by rule, never the whole queue at once (private-repo deployment proposal)
- [ ] **Agent-ops metric floor** — dwell time (anomaly → human awareness),
      coverage (fraction of agent outputs a human reviewed), and
      explainability-by-trigger-ID (every agent output cites the ID of its
      triggering event, a mandatory loop-contract field) (private-repo deployment proposal)
- [ ] **Compartmentalization worked example** — the most-exposed agent gets
      the fewest permissions (write-only into a quarantine zone), the
      most-privileged agent gets no public egress, and promotion out of
      quarantine is human-gated: agent proposes + safety report, human
      approves, agent executes (private ADR-031)
- [ ] **Human-gated model experimentation + dual-LLM review** — model
      adoption is a human judgment recorded as a reviewable config diff,
      never a runtime switch; critical calls may use a producer→reviewer
      pair (always different models, bounded at exactly two) — manual first,
      automated per task only after stabilization (private ADR-032)
- [ ] **AI vendoring** — for a small, unmaintained, poorly-scored dependency,
      reimplement the subset of functionality actually used instead of
      keeping the dependency (Anthropic Zero-Trust eBook). **Unproven here**
      — export only after it has been practiced at least once in the private
      monorepo
- [ ] **Layering rule** for agent/platform rollouts (operating-model doc):
      foundational ops/observability ships first; every subsequent phase is
      sized to be immediately usable — no functionality that idles behind
      unmet dependencies (private-repo deployment proposal)

## Non-goals

- Shipping application source code
- Runtime agent governance (see Microsoft Agent Governance Toolkit for that layer)
- Competing with full RAG/agent platforms (SurfSense, Dify, etc.)

## Cadence

- Target: **monthly** or **milestone** releases when standards change materially
- Minimum: **quarterly** sync if no changes (changelog notes "maintenance — no content delta")

## Seeded issues

On first GitHub publish, create issues from `.github/labels.md` with label `roadmap`.
