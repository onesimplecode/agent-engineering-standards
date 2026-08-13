# Worked Example: Honest CI Limits (friction, not barriers)

CI security and permission guards catch **accidents and casual drift**. They
do not stop a determined author who edits the workflow or guard script in the
same PR. Say that limit out loud — in workflow headers, script docstrings, and
`AGENTS.md` — so reviewers know what still needs a human look.

Comparative references (ideas only, no code copied):
[`MadsLorentzen/ai-job-search`](https://github.com/MadsLorentzen/ai-job-search)
CI header comments + `security_guards.py`; this repo's own
`scripts/agent-permission-guard.py` (TR-SEC-010) already states the same
honest limit.

## Minimal fixtures in this folder

| File | What it demonstrates |
|---|---|
| `ci-header.example.yml` | Workflow header: permissions block, SHA-pinned action comment, "what CI will not do" |
| `gitignore.example` | Personal-data ignore with a narrow negation allowlist — widening the allowlist is loud |

These are **documentation fixtures**, not live workflows. Copy the comment
shape into real `.github/workflows/` and `.gitignore` files; do not expect
this YAML to run as-is in this repo's CI.

## Honest limit (Impossible vs. Tedious)

| Control | Class | Real backstop |
|---|---|---|
| Drift guard / allowlist script | Friction | Branch protection + human review of guard+target diffs |
| Workflow `permissions:` + SHA pins | Friction | Same — a PR can edit the workflow |
| `.gitignore` personal-data rules | Friction | Review of gitignore diffs; secret scanning |

A barrier would be something the author cannot widen in the same commit
(e.g. org-level required checks they do not control). Most repo-local CI
guards are friction — name the backstop.

## Trace to standards artifacts

| Artifact | Location |
|---|---|
| Guard pattern + honest limit | `AGENTS.md` — "Guard Pattern", "Honest CI Limits" |
| Impossible vs. tedious | `templates/threat-model.md`, `AGENTS.md` |
| SHA-pinned / least-privilege CI | `registry/tr-registry.yaml` (TR-SEC-009), `.github/workflows/release-check.yml` |
| Attribution | `ATTRIBUTIONS.md` (`MadsLorentzen/ai-job-search`) |
