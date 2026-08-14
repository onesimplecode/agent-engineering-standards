# Contributing

Thank you for interest in Agent Engineering Standards. This repository is a
**standards toolkit** — templates, requirement registry, and reference scripts for
building auditable agent-assisted software workflows. It is not a supported product.

## Scope

In scope:

- Improvements to templates, registry entries, scripts, docs, and worked examples.
- Bug reports with reproduction steps and affected file paths.
- Proposals for new TR-IDs or governance patterns with rationale.

Out of scope:

- Support for maintainer-private applications not published in this repository.
- Generic "make AI better" requests without a concrete standards gap.
- Requests to add full application frameworks or duplicate `agent-skills` / `AGENTS.md`.
- Domain-specific agent modes (e.g. job-search or other single-vertical
  workflows). Patterns must generalize across projects to belong here.

## Before You Open an Issue

1. Search existing issues and the roadmap (`ROADMAP.md`).
2. State the **failure mode** you are trying to prevent (e.g. model-string drift, PII routing mistake).
3. For bugs: include version/tag, steps to reproduce, expected vs actual behavior, and evidence
   (command output, file paths).

Reports that lack reproduction evidence or appear to be bulk AI-generated without project-specific
detail may be labeled `needs-evidence` or `low-effort-ai` and closed without deep triage.

## Pull Requests

1. Fork and branch from `main`.
2. Keep changes focused; one concern per PR when possible.
3. Fill out the PR template completely.
4. Run checks locally:

   ```bash
   python3 scripts/public-export-check.py .
   python3 -m py_compile scripts/*.py
   ```

5. If you adapt third-party content, update `ATTRIBUTIONS.md` with source URL and license.

## Response Expectations

Maintainers release on a **periodic, roadmap-driven cadence**. There is no SLA on issue or PR
response. See `ROADMAP.md` for planned work.

## Code of Conduct

Be specific, constructive, and respectful. Debate standards on merit — cite failure modes and
trade-offs, not preferences alone.
