# Integrating with agent-skills

This repository **complements** [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)
(and skill collections like it) — it does not compete with them. The two operate
at different layers, and they compose.

## The layer split

| | agent-skills | agent-engineering-standards (this repo) |
|---|---|---|
| Unit | A skill: a task-level playbook ("how to do X well") | A requirement: a stable, ID'd constraint ("what must always hold") |
| Scope | Per-task, invoked when the task matches | Cross-cutting, applies to every task |
| Enforcement | Instruction-following by the agent | Deterministic scripts and CI gates where possible (`scripts/`), documented conventions elsewhere |
| Evolution | New skills for new tasks | IDs are permanent; text evolves under changelog discipline |

A skill tells an agent how to do a code review or write a commit message.
A standard says no hardcoded secrets (TR-SEC-001), PII routes to local models
only (TR-SEC-003), every agent node declares a loop contract (TR-AGT-003) —
regardless of which skill is running.

## Integration patterns

**1. Cite TR IDs inside skills.** When a skill's instructions touch a governed
area, reference the requirement ID instead of restating (and eventually
forking) the rule. A testing skill that says "follow TR-TEST-001" inherits
registry updates for free, and reviewers can trace which constraint applied.

**2. Generate editor/agent context from the registry.** The registry is
machine-readable precisely so tool-specific context can be derived rather than
hand-maintained. `scripts/cursor-rules-adapter.py` is the working example for a
single tool: it exports the coding-relevant registry subset as Cursor `.mdc`
rules (pregenerated copy in `examples/cursor-rules/`), with CI failing on drift.
`scripts/llms-txt-generator.py` generalizes the same pattern to any agent
framework rather than one tool: it exports the registry, `agents/*.md`,
`templates/*.md`, and `scripts/*.py` as a single `llms.txt` at repo root,
following the emerging llms.txt convention (https://llmstxt.org) some
agent/LLM tools already look for by default — also drift-gated in CI.
The same underlying pattern applies to any tool that consumes context files —
skills handle the task layer, generated rules/manifests pin the constraint
layer underneath.

**3. Gate skill output with the governance artifacts.** Whatever skill
produced a change, the same checks apply: the completion self-critique
(`templates/completion-checklist.md`), the reviewer role spec
(`agents/reviewer.md`), and the deterministic scanners
(`check-config-consistency.py`, `debt-report.py`) in CI. Skills raise the
ceiling of what an agent does well; the gates hold the floor.

## Boundary (by design)

Per `CONTRIBUTING.md`, this repo does not accept task playbooks or skill
collections — contribute those to a skills repository. What belongs here is
the constraint layer: registry entries, templates, deterministic checks, and
adapters that export them into other tools' formats.

## Multi-runtime thin pointers (ROADMAP v0.9)

When integrating with more than one coding-agent harness, prefer **one
canonical instruction tree** and short per-runtime pointers over forked
copies of the same skill/mode prose. Skills remain the task layer; this
repo's registry and generated manifests (`cursor-rules-adapter.py`,
`llms.txt`) remain the constraint layer.

Minimal worked example: `examples/thin-pointer/` — one canonical checklist
plus short `AGENTS` and Cursor-rule wrappers that point at it. Comparative
exemplars (not shipped): `santifer/career-ops`, `MadsLorentzen/ai-job-search`.

**Plugin / skill trust:** third-party skill markdown is untrusted data
(TR-SEC-005). See `examples/plugin-skill-trust/` and `AGENTS.md`.

**Deferred (ROADMAP Backlog — unscheduled):** system vs user path data
contract — wait for a private consumer that needs safe auto-update of agent
tooling before shipping a synthetic updater example.
