# Issue labels (TR-PUB-004)

Apply these labels in the public GitHub repository. Create them in repo Settings → Labels.

| Label | Color suggestion | When to use |
|-------|------------------|-------------|
| `bug` | #d73a4a | Reproducible defect |
| `docs` | #0075ca | Documentation only |
| `question` | #d876e3 | Usage question |
| `proposal` | #a2eeef | Standards change proposal |
| `needs-evidence` | #fbca04 | Missing repro or version |
| `low-effort-ai` | #ededed | Generic AI report; close if not improved |
| `wontfix-scope` | #ffffff | Out of scope |
| `good-first-issue` | #7057ff | Small bounded task |
| `roadmap` | #0e8a16 | Tracked in ROADMAP.md |

## Triage rules

1. New issues without required template fields → `needs-evidence`, request update.
2. Duplicate generic AI checklists → `low-effort-ai`, close with link to CONTRIBUTING.md.
3. App-specific support requests → `wontfix-scope`, redirect to private projects.
4. Accepted proposals → link to roadmap issue or milestone.

## Seeded roadmap issues

Open one issue per candidate in the "Next up" table of `ROADMAP.md`, labelled
`roadmap`, with the candidate's evidence gate in the body so an outside reader
can see what would unblock it. Kept as a pointer rather than a duplicated list —
the roadmap is the single source of truth for what is next.
