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

## v0.7 — Agentic security & operations patterns

Released 2026-07-26 (`v0.7.0`).

From the 2026-07-13 Zero-Trust-for-AI-Agents review (private ADRs: private-repo
ADR-030/031/032, private-repo ADR-018, and a private-repo deployment proposal).
The review identified nine candidate exports; three were export-ready and
shipped in this release, six were design-only and deferred — see v0.8 (two of
the six, now with running evidence) and Backlog (the remaining four) below.

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

## v0.8 — Verified isolation & ground-truth testing

Released 2026-07-31 (`v0.8.0`).

From a private-repo agent-platform deployment (private ADR-013, ADR-014;
2026-07-25 to 2026-07-29) — the first case of a `compartmentalization`-shaped
design (private ADR-031, v0.7's own roadmapped item above) actually built,
running, and hands-on verified rather than design-only. Three exports, one of
them genuinely new content rather than a graduation:

- [x] **Compartmentalization worked example** (graduates from v0.7's
      roadmapped item, private ADR-031 → private ADR-013/014). Two-layer
      isolation for a multi-agent system sharing one backing service: a
      tool-registry scope (what's *offered* to each agent's own reasoning —
      distinct credentials per agent, server-side authorization) sitting
      above a data-layer scope (what's *reachable* even if the authorization
      layer has a bug — e.g. per-agent DB roles). The two are defense in
      depth, not redundant: neither alone is the full mitigation, extending
      TR-SEC-010's least-agency framing from single-agent tool grants to
      multi-agent tool + data boundaries. Also carries the corrected version
      of the private ADR-031 promotion-gate story: a human-approval step was
      dropped after review found it protected an action that wasn't the
      actual security-relevant moment — kept in the worked example's README
      as a caution against copying a control's *conclusion* without
      re-checking whether its *reasoning* still holds.
      Shipped as a **new registry entry** (TR-SEC-013 — a new ID read better
      than amending TR-SEC-010, since multi-agent tool+data isolation is a
      distinct claim from single-agent tool-grant restriction, matching how
      TR-SEC-011/012 were each given their own entry rather than folded into
      an existing one): `registry/tr-registry.yaml`,
      `examples/compartmentalized-agents/` (`isolation.py` + a test proving
      the data layer blocks a deliberately misconfigured tool layer —
      the actual defense-in-depth proof, not just that both layers exist),
      `AGENTS.md` "Compartmentalized Multi-Agent Isolation" section,
      `docs/requirements-implementation-map.md` row.
- [x] **Ground-truth verification for agent security-property claims** — new
      pattern, not previously roadmapped. A claim about an agent's own
      behavior, obtained only by asking the agent (chat transcript) — "do you
      have tool X," "do you remember Y" — is not verification evidence for a
      security-relevant property (isolation, permission boundary, memory
      scoping). Verify against the system's own ground truth instead (the
      target API's own list/read endpoint, a DB row, a server log line),
      independent of what the agent under test reports. Motivated by two real
      false passes in the ADR-014 spike: an isolation check that "passed" only
      because the test question was routed to the wrong backend entirely (not
      the one actually under test), caught only by querying the real memory
      store's API directly instead of trusting the chat reply. This is a
      sharper, agent-specific instance of the existing "verify before
      referencing" / zero-hallucination discipline, applied to runtime
      behavior claims rather than static code symbols.
      Shipped as **TR-TEST-007** (new entry — distinct from TR-TEST-006's
      write-effect verification, this covers self-report vs. ground truth for
      a behavioral/security claim) in the "Testing" section; a checklist line
      item in `templates/completion-checklist.md`; the
      compartmentalized-agents example extended with `SelfReportingAgent`
      (`isolation.py`) and a test showing its self-report gives a false pass
      on an isolation leak that `ToolRegistry.list_tools()` — ground truth —
      catches.
- [x] **Layering rule** (graduates from v0.7's roadmapped item, second
      exemplar: private ADR-013's Phase A → A.5 → B → C → D rollout table,
      alongside the existing private deployment-proposal citation).
      Foundational/shared infrastructure ships first; every subsequent phase
      is immediately usable on arrival — no functionality idles behind an
      unmet dependency, and no phase is "mostly done" before the next starts.
      Shipped as a new "Rollout Sequencing" section in
      `docs/ai-engineering-operating-model.md` with a genericized phase-table
      shape, plus a `docs/requirements-implementation-map.md` row —
      documented pattern, no new TR-ID (matches other "Documented"-only rows
      in that map).

All three shipped. Promotion bar, consistent with v0.7's rule: exported only
once the private implementation has *running, hands-on evidence* behind it,
not just an accepted design ADR — met here by ADR-014's spike outcome
(2026-07-29).

## v0.8.1 — Reviewer evidence spot-check

Released 2026-08-03 (`v0.8.1`). Patch release — no new roadmap theme.

- [x] `agents/reviewer.md` requires spot-checking completion-checklist
      file:line citations against the diff (blocking on unsupported claims)

## Backlog — unscheduled

Deferred from the 2026-07-13 Zero-Trust-for-AI-Agents review, design-stage
only as of 2026-07-13 with no running implementation cited since. Not
attached to any version — promotion requires the same bar as v0.7/v0.8: an
operating track record in the private monorepo (commits, tests, hands-on
evidence), not just an accepted design ADR.

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

## Non-goals

- Shipping application source code
- Runtime agent governance (see Microsoft Agent Governance Toolkit for that layer)
- Competing with full RAG/agent platforms (SurfSense, Dify, etc.)

## Cadence

- Target: **monthly** or **milestone** releases when standards change materially
- Minimum: **quarterly** sync if no changes (changelog notes "maintenance — no content delta")

## Seeded issues

On first GitHub publish, create issues from `.github/labels.md` with label `roadmap`.
