# Governance Review — Cycle [N] — [Date]

**Operationalizes:** TR-GOV-006 (ISO/IEC 42001 clause 9.3 — management review).

Reviews are triggered by: (a) any app's tier graduation (POC → Local Production →
Cloud Production), or (b) at minimum every 90 days, whichever comes first.

Use this template for each release, tier graduation, or recurring standards
review. If this is the first review for a project, record it as Cycle 1.

## Scope

Which apps and org-level documents were reviewed this cycle?

## Status of Previous Cycle's Open Items

| Item (from prior cycle) | Status | Notes |
|---|---|---|
| | | |

## New Findings

Use a consistent severity/evidence/recommendation structure. Focus on drift
between written policy (`AGENTS.md`, `registry/tr-registry.yaml`, ADRs, templates)
and actual implementation.

| Finding | Severity | Affected app(s) | Recommendation |
|---|---|---|---|

## Tooling Output

Run and attach results:

```
python3 scripts/check-config-consistency.py
python3 scripts/debt-report.py
python3 scripts/public-export-check.py .
```

## Maturity Checklist Deltas

For each app with a `docs/maturity-checklist.md`, note any status changes since
the last review.

| App | Objective | Previous status | New status | Reason |
|---|---|---|---|---|

## Updates to Org-Level Governance

- [ ] `registry/tr-registry.yaml` changes (new/superseded TR-IDs)
- [ ] `AGENTS.md` changes
- [ ] New or updated ADRs

## Actions for Next Cycle

Specific, owned, dated.

## Next Review Trigger

- Next tier graduation expected: [app, target date]
- 90-day fallback date: [date]
