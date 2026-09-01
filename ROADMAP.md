# Roadmap

Releases are **curated and periodic**, not continuous dumps of unrelated work.
Shipped detail lives in [`CHANGELOG.md`](CHANGELOG.md); this file is about what
comes next.

**How something gets onto this page.** Patterns are extracted from a private
monorepo where they are actually running. A pattern is exported only once it has
running, hands-on evidence behind it — commits, tests, a real incident it caught
— not just an accepted design document. That bar is why the backlog moves
slowly and why the examples here are drawn from real failures rather than
invented for illustration.

**Have a failure mode this doesn't cover?** That is the most useful issue you
can open — see [`CONTRIBUTING.md`](CONTRIBUTING.md). Backlog items below are
unscheduled by default; a concrete use case is a legitimate reason to reprioritize.

## Next up

Candidates for the next release, in priority order. Each names the evidence gate
it is still waiting on.

| Candidate | What it adds | Waiting on |
|---|---|---|
| **System vs. user path data contract** | Versioned allowlists of system-updatable vs. user-owned paths, with a deterministic CI non-overlap check — safe auto-update of agent tooling that cannot touch user data | A private consumer that needs it; deferred from v0.9 rather than inventing a synthetic updater |
| **Agreement-rate-gated authority promotion** | The measurable form of an advisory-first trust ramp: agent verdicts run advisory while human-agreement rate is measured; promotion to blocking cites the rate rule by rule, never the whole queue at once | An operating track record of measured agreement rates |

## Recently shipped

| Version | Date | Theme |
|---|---|---|
| [v0.13.0](CHANGELOG.md#0130---2026-09-01) | 2026-09-01 | Fail-closed named agent authority manifests (TR-AGT-012), promoted from a tested private consumer; release-publisher repair and cache hygiene |
| [v0.12.0](CHANGELOG.md#0120---2026-08-28) | 2026-08-28 | Frozen, generated tool contracts (TR-AGT-010); disposition loop-contract field (TR-AGT-003 field 6); hybrid deterministic-then-agentic classification stage tagging (TR-AGT-011); graded outlet confidence (TR-SEC-015) — all four promoted from running private-monorepo consumers with passing drift-guard tests |
| [v0.11.0](CHANGELOG.md#0110---2026-08-21) | 2026-08-21 | Credential-isolated broker pattern (TR-SEC-014), promoted from a running Hermes reviewer integration with real CI, lease, and restart-failure evidence |
| [v0.10.0](CHANGELOG.md#0100---2026-08-13) | 2026-08-13 | Announcement-ready README and roadmap, `AGENTS.starter.md`, rename to Agent Engineering Standards, `TECH-DEBT` tag, drift-guard tests for the README's own factual claims |
| [v0.9.0](CHANGELOG.md#090---2026-08-13) | 2026-08-13 | Multi-runtime instruction source-of-truth, plugin-skill trust, honest CI limits, SSRF allowlist |
| [v0.8.1](CHANGELOG.md#081---2026-08-03) | 2026-08-03 | Reviewer spot-checks completion-checklist citations against the diff |
| [v0.8.0](CHANGELOG.md#080---2026-07-31) | 2026-07-31 | Verified multi-agent isolation; ground-truth verification of agent security claims |

Earlier releases (v0.1–v0.7) established the registry, governance templates,
reference scripts, CI demo workflows, cross-tool adapters, and the security
baseline. Full detail in [`CHANGELOG.md`](CHANGELOG.md).

## Backlog

Unscheduled. Promotion requires the evidence bar described at the top of this
file.

<details>
<summary><strong>Agent operations and trust ramps</strong></summary>

- **Agent-ops metric floor** — dwell time (anomaly → human awareness), coverage
  (fraction of agent outputs a human reviewed), and explainability-by-trigger-ID
  (every agent output cites the ID of its triggering event, as a mandatory
  loop-contract field).
- **Human-gated model experimentation + dual-LLM review** — model adoption is a
  human judgment recorded as a reviewable config diff, never a runtime switch;
  critical calls may use a producer→reviewer pair (always different models,
  bounded at exactly two), manual first and automated per task only after
  stabilization.

  **Progress (2026-08-15):** LumiaForge's Hermes `pr-reviewer` is a verified
  producer-independent reviewer using GPT-5.6 Terra after a coding-model PR,
  with deterministic CI gates, credential isolation, and a successful real-PR
  review. This is evidence for the reviewer half of the pattern, not completion:
  the roadmap item remains open until a distinct coding-agent path is established,
  model changes are human-gated, the exactly-two/different-model invariant is
  machine-checked, and reviewer agreement is measured before authority promotion.

  **Progress (2026-08-30):** three of four gates now met. (1) A distinct coding-agent
  path exists — Hermes' `coder` profile (ADR-024) is a separate producer from
  `pr-reviewer`. (2) The producer/reviewer model pairing was found to have silently
  collapsed onto one model (`coder` and `pr-reviewer` both defaulted to
  `z-ai/glm-5.3-flash`) and was corrected to distinct models
  (`pr-reviewer` → `x-ai/grok-4.6`) via a reviewable config-diff PR, not a runtime
  switch. (3) The exactly-two/different-model invariant is now machine-checked —
  `scripts/check-model-diversity.py`, run in CI on every PR/push/weekly
  (`governance-lint.yml`, private model-diversity guard) — so this class of drift can't recur silently.
  Still open: reviewer agreement measured before authority promotion. Until that
  gate closes, this item stays in Backlog, not Recently Shipped.

- **Explicit precision/recall stance for AI review agents** — a reviewer's docs
  or config must state, as a declared setting, which side of the
  precision/recall tradeoff it optimizes for, so downstream consumers don't
  infer a stance from behavior. New TR-ID and registry entry; needs a private
  consumer practicing it first — a candidate PR-review agent in the private
  monorepo currently has no such disclosure and no eval harness to measure it
  against — before export, per this file's evidence bar.

</details>

<details>
<summary><strong>Provenance and classification</strong></summary>

- **State-media / outlet-risk tier** — a distinct risk dimension beyond the
  reputability grading TR-SEC-015 shipped in v0.12.0 (see `CHANGELOG.md`);
  needs a private consumer with an actual use case for classifying
  state-affiliated or risk-flagged outlets, not just reputability. TR-SEC-015's
  own curated-allowlist approach is the likely shape, but this dimension has
  no consumer or use case in the private monorepo yet.
- **Confidence-gated stage override** — in a hybrid deterministic-then-agentic
  classification pipeline (TR-AGT-011, shipped in v0.12.0), a later, costlier
  stage overriding an earlier deterministic stage's result on higher
  confidence — rather than only short-circuiting past it, which is as far as
  TR-AGT-011 goes. Needs a private consumer with a real override path (and a
  reason a deterministic stage's result should ever be overturned) before
  export, not just the stage-tagging discipline already shipped.

</details>

<details>
<summary><strong>Cost and dependency hygiene</strong></summary>

- **Content-hash LLM-call dedup for cost stampede control** — cache or coalesce
  identical prompts so concurrent callers share one invocation. Export only after
  it is practiced with measurable cost impact.
- **AI vendoring** — for a small, unmaintained, poorly-scored dependency,
  reimplement the subset actually used instead of keeping the dependency.
  **Unproven here** — export only after it has been practiced at least once.

</details>

## Non-goals

- Shipping application source code
- Runtime agent governance (see Microsoft Agent Governance Toolkit for that layer)
- Competing with full RAG/agent platforms (SurfSense, Dify, etc.)
- Domain-specific agent modes (e.g. job-search workflows) — see `CONTRIBUTING.md`

## Cadence

- Target: **monthly** or **milestone** releases when standards change materially
- Minimum: **quarterly** sync if no changes (changelog notes "maintenance — no
  content delta")
