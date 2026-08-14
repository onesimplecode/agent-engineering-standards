# Maintainer Release Guide

This document describes the steps for cutting a new release of `agent-engineering-standards`.
Releases are periodic and curated — see `ROADMAP.md` for scope of each version.

## Release triggers

Cut a release when:
- All roadmap items for the next version are implemented and reviewed.
- A significant content change warrants a new baseline (at maintainer discretion).
- Quarterly cadence fires with no material changes (changelog notes "maintenance — no content delta").

## Pre-release checklist

**Before starting this checklist**, run the private-repo leak scan from the
source monorepo root (not shipped here — this repo's own CI cannot see private
content, so it cannot catch this class of issue):

```bash
python3 scripts/private-public-export-check.py public-standards
```

This catches private app/project names, local paths, and career artifacts that
may have entered staged content since the last release (e.g. copied from a
private ADR or roadmap note). A v0.5.0 release shipped two private app names
in prose before this step was made mandatory here — content-pattern checks
alone (this repo's `detect-secrets` step) do not cover project-name leaks.

### 1. Verify staging content

Confirm the working tree reflects the intended release state:
- All content changes for this version are present and finalized in the repository.
- No unintended edits, debug artifacts, or uncommitted drafts remain.
- `git status` is clean (or staged changes are intentional release edits only).

### 2. Run CI checks locally

From this repository's root (use a virtual environment to avoid PEP 668 conflicts):

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install "pytest" "detect-secrets>=1.4.0,<2.0.0"
python3 scripts/public-export-check.py .
python3 -m py_compile scripts/*.py
detect-secrets scan \
  --exclude-files '^templates/' \
  --exclude-files '^examples/' \
  | python3 -c "import json,sys; r=json.load(sys.stdin).get('results',{}); print('Potential secrets found -- run detect-secrets scan locally to audit' if r else 'OK -- no secrets detected.'); sys.exit(1 if r else 0)"
python3 scripts/cursor-rules-adapter.py --out examples/cursor-rules/.cursor/rules --check
python3 scripts/llms-txt-generator.py --check
python3 -m pytest tests -q
```

All checks must pass before proceeding. Repeat this step after completing steps 3–5 to
catch any new patterns introduced in `CHANGELOG.md` or `ROADMAP.md`.

### 3. Update `CHANGELOG.md`

Add a dated `[X.Y.Z]` section at the top of the changelog with Added / Changed / Fixed /
Removed subsections. Update the comparison URLs at the bottom:

```
[Unreleased]: https://github.com/onesimplecode/agent-engineering-standards/compare/vX.Y.Z...HEAD
[X.Y.Z]: https://github.com/onesimplecode/agent-engineering-standards/compare/vA.B.C...vX.Y.Z
```

### 4. Update `ROADMAP.md`

Move shipped candidates out of "Next up" into the "Recently shipped" table with
their version and date, re-rank the remaining candidates, and promote any backlog
item that now has running evidence behind it. Shipped detail belongs in
`CHANGELOG.md`, not here.

### 5. Review `ATTRIBUTIONS.md`

Confirm any adapted third-party content introduced since the last release is attributed.

## Tagging and publishing

```bash
git add -p                            # stage release changes
git commit -m "chore: release vX.Y.Z"
git tag vX.Y.Z
git push origin main                  # or merge a release branch via PR if branch protection is enabled
git push origin vX.Y.Z
```

Then create a GitHub Release from the tag. Use the CHANGELOG section for that version
as the release body.

## Version numbering

Follows SemVer-lite (`MAJOR.MINOR.PATCH`):

| Bump | When |
|------|------|
| PATCH | Corrections to existing content, wording fixes |
| MINOR | New templates, registry entries, scripts, or examples |
| MAJOR | Breaking changes to template format or TR registry schema |

## Announcement prep (one-time)

The repository has been public since v0.1.0; these are the discovery and
presentation steps that a release alone does not cover, done once ahead of a
public announcement.

- Create issues from `.github/labels.md` with label `roadmap`, seeded from the
  "Next up" section of `ROADMAP.md`.
- Confirm the badge URLs at the top of `README.md` resolve against the published
  repository path (`onesimplecode/agent-engineering-standards`).
- Set the repository **About** description — it is what appears in GitHub search
  results and on the profile, and most visitors read it before the README:

  > This repo gives your AI coding agent rules it reads and your CI the checks
  > that fail the build when it takes a shortcut anyway — skipped tests, widened
  > permissions, fail-open model output.

- Set repository **topics** (GitHub's actual discovery surface for this
  category). Verified populations as of 2026-08-13:

  | Topic | Why |
  |---|---|
  | `agentsmd` | 46 repos — the live `AGENTS.md` topic; closest peer set |
  | `agents-md-template` | 21 repos — peers are Groundwork, neckbeard, fable-md; fits because this repo ships a copy-paste `AGENTS.starter.md` |
  | `ai-agents`, `claude-code`, `cursor`, `ai-coding-assistant` | Audience/harness discovery |
  | `llm-security`, `prompt-injection`, `ai-governance`, `ci-cd` | Failure-domain discovery |

- Consider submitting to the curated `awesome-agents.md` list, findable under the
  [`agentsmd` topic](https://github.com/topics/agentsmd) — a curated-list entry is
  the highest-leverage inbound link in this niche. Confirm the list's own
  submission rules before opening a PR.

## Post-release

- Confirm CI passes on the tagged commit.
- Verify the GitHub Release page renders correctly.
- Check that the comparison URL in `CHANGELOG.md` resolves on GitHub.
- Verify the published tree matches the release source exactly — compare with a
  content-based diff (`diff -r`, or `rsync -rcn --delete`), not a size/mtime quick-check.
  The v0.3.0 publish silently dropped a `ROADMAP.md` checkbox update because
  `[ ]` → `[x]` is byte-size-neutral and the sync compared only size and mtime.
