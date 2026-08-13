# Worked Example: Thin-Pointer Multi-Runtime Instructions

One **canonical** instruction tree; each agent harness gets a **short pointer**
instead of a forked copy of the same workflow prose. Drift between
`AGENTS.md`, Cursor rules, Codex skills, and other entry files is a silent
governance failure.

Comparative exemplars (ideas only): `santifer/career-ops`,
`MadsLorentzen/ai-job-search`. This fixture is minimal documentation — not a
claim that every private app already dual-runs two harnesses.

| Path | Role |
|---|---|
| `canonical/review-checklist.md` | Full SoT for a tiny review workflow |
| `wrappers/AGENTS.snippet.md` | Short AGENTS-style pointer |
| `wrappers/cursor-rule.snippet.mdc` | Short Cursor-rule pointer |

```bash
python3 -m pytest tests/test_thin_pointer_example.py -q
```

## Rule of thumb

| Put here | Put in the canonical file |
|---|---|
| Path to the SoT + one sentence | Numbered steps, rubrics, long policy |
| Harness-specific discovery metadata (globs, frontmatter) | Shared behavioral content |

## Trace

| Artifact | Location |
|---|---|
| Rule | `AGENTS.md` — Thin-pointer multi-runtime instructions |
| Skills vs standards layers | `docs/agent-skills-integration.md` |
| ROADMAP | v0.9 |
