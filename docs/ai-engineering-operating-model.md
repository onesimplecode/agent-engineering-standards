# AI Engineering Operating Model

LumiaForge treats AI-assisted development as a governed engineering system, not
as ad hoc prompting. The operating model has four layers:

1. **Requirements** — stable, named expectations in `registry/tr-registry.yaml`.
2. **Roles** — bounded agent responsibilities in `AGENTS.md` and `agents/`.
3. **Artifacts** — ADRs, impact assessments, maturity checklists, and eval plans.
4. **Checks** — deterministic scripts and CI that catch drift before review.

## Why This Exists

AI agents are useful but failure-prone. Common failure modes include:

- skipping tests or edge cases;
- inventing APIs or file paths;
- mixing private and public data contexts;
- treating retrieved content as instructions;
- creating background triggers without review;
- leaving documentation and config out of sync.

This repo encodes controls for those failures.

## Operating Loop

```text
Requirement -> Role contract -> Design artifact -> Implementation -> Deterministic check -> Review -> Release
```

The loop is deliberately boring. The point is to make agent output inspectable
by humans and other agents.

## Design-Time Controls

- **Loop contracts** require input schema, output schema, exit condition, and
  resource budget before building multi-step agent workflows.
- **Trigger classification** forces event-driven, scheduled, and user-initiated
  work to be named before implementation.
- **Impact assessment** captures affected parties, data classes, harms, and
  mitigations for AI-affecting decisions.
- **ADR lifecycle** preserves why a decision was made and how it can be
  superseded later.

## Rollout Sequencing

Multi-phase agent or platform builds ship in **layers**, not a single
big-bang release: foundational, shared infrastructure ships first, and every
subsequent phase is immediately usable the moment it lands — no phase should
sit "mostly done," idling behind a later phase that hasn't been built yet.

| Phase | Ships | Immediately usable as |
|---|---|---|
| Foundations | Shared infra (auth, storage, observability, backup) | The measurement/ops base every later phase is built on |
| Capability A | First agent/workflow, fully wired end to end | A working, narrow slice — not a stub |
| Capability B | Second agent/workflow, reusing Foundations | Independently usable even if a later Capability C is delayed |
| Wrap-up | Docs, CI, reproducibility | A rebuildable system, not tribal knowledge |

Each phase's own tests pass before the next phase starts — no phase is
"mostly done." Documentation updates land in the same change as the phase
they describe, not batched at the end.

## Repo-Time Controls

- `scripts/check-config-consistency.py` catches retired model strings and
  config/documentation drift.
- `scripts/debt-report.py` surfaces `LUMIA-DEBT:` and `POC-EXCEPTION:` tags.
- `scripts/public-export-check.py` validates public repo hygiene before release.

## Role-Time Controls

- Developer agents implement and produce a change summary.
- Reviewer agents inspect correctness, security, privacy, tests, and ADR
  completeness from fresh context.
- Private researcher agents handle sensitive analysis locally.
- Public researcher agents only handle non-sensitive public sources.

## What This Is Not

This is not a runtime agent framework, a hosted product, or a replacement for
skills/rules ecosystems. It is the design-time and repo-time governance layer
that can sit underneath those tools.
