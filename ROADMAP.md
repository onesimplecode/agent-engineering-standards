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

The v0.11.0 release includes the credential-isolated broker pattern, promoted from a running
Hermes reviewer integration with real CI, lease, and restart-failure evidence.

Candidates for the next release, in priority order. Each names the evidence gate
it is still waiting on.

| Candidate | What it adds | Waiting on |
|---|---|---|
| **System vs. user path data contract** | Versioned allowlists of system-updatable vs. user-owned paths, with a deterministic CI non-overlap check — safe auto-update of agent tooling that cannot touch user data | A private consumer that needs it; deferred from v0.9 rather than inventing a synthetic updater |
| **Frozen agent protocol** | Makes "stable tool contract" enforceable instead of aspirational: additive-forever field semantics, a `protocol_version` on every response *and error*, and a spec **generated from live operation definitions** so docs and code cannot structurally drift | A frozen surface in the private monorepo with conformance tests passing against a live mount |
| **Agreement-rate-gated authority promotion** | The measurable form of an advisory-first trust ramp: agent verdicts run advisory while human-agreement rate is measured; promotion to blocking cites the rate rule by rule, never the whole queue at once | An operating track record of measured agreement rates |

## Recently shipped

| Version | Date | Theme |
|---|---|---|
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

- **Disposition contract** — triage agents emit a structured disposition
  (query / think / report) as a loop-contract output field, extending TR-AGT-003.
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

</details>

<details>
<summary><strong>Provenance and classification</strong></summary>

- **Graded source confidence** — optional outlet-tier / state-media risk metadata
  alongside the fail-closed TR-SEC-011 trust mapping. Tiers inform weighting and
  disclosure; they must never upgrade an unknown source to trusted. Needs a
  private consumer that stores and retrieves graded confidence with a drift-guard
  test.
- **Hybrid keyword → ML → LLM classification with source-tagged confidence** —
  each result carries which stage produced it (`keyword` / `ml` / `llm`);
  deterministic stages run first; the LLM may override only on higher confidence.
  Reinforces "deterministic checks before agent judgment" and TR-SEC-012.

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
