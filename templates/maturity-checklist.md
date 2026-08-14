# Maturity Checklist: [App Name]

**Last updated:** YYYY-MM-DD
**Current tier:** [POC | Local Production | Cloud Production]
**Operationalizes:** TR-GOV-004 (per-app Statement of Applicability, modeled on ISO/IEC 42001 Annex A)

This checklist maps these standards' governance mechanisms to the 9 ISO/IEC 42001
Annex A control objectives. For each objective, record whether it applies to this
app at its current tier, its status, the evidence, and — for anything not yet
Met — the tier at which it must be closed.

**Status values:** `Met` | `Partial` | `Gap` | `N/A`

Update this checklist at every tier graduation and at each governance review
(TR-GOV-006, `templates/governance-review.md`). Use `scripts/debt-report.py` to
pull open `TECH-DEBT:` / `POC-EXCEPTION:` items into the Evidence column.

| # | Annex A Objective | Standards Mechanism | Applicable | Status | Evidence | Target for closure |
|---|---|---|---|---|---|---|
| A.2 | AI policies | `AGENTS.md`, `registry/tr-registry.yaml`, app README or local policy docs | | | | |
| A.3 | Internal organization | Agent role contracts in `agents/` plus app-specific ownership notes | | | | |
| A.4 | Resources for AI systems | LLM provider/model choices documented in ADRs, config examples, or app README | | | | |
| A.5 | AI system impact assessment | `templates/ai-impact-assessment.md`, attached to ADRs per TR-GOV-005 | | | | |
| A.6 | AI system lifecycle | ADRs (`docs/decisions/`), TDD (TR-TEST-001/002), evals (TR-TEST-005), CI quality gate | | | | |
| A.7 | Data for AI systems | TR-SEC-002 (PII at rest), TR-SEC-003 (local-LLM PII routing), TR-SEC-005 (untrusted retrieved content) | | | | |
| A.8 | Information for interested parties | `docs/case-study.md`, README, retrospectives (`docs/retrospectives/`) | | | | |
| A.9 | Use of AI systems / human oversight | Human approval steps in ADRs, impact assessments, PR template, or local agent policy | | | | |
| A.10 | Third-party / supplier relationships | Provider/model ADRs, `ATTRIBUTIONS.md`, license review notes, `scripts/check-config-consistency.py` (TR-GOV-001) | | | | |

## Open items

Pull from `python3 scripts/debt-report.py` (filter to this app's paths) and list
anything relevant to a `Partial` or `Gap` row above:

- [ ]

## Review history

| Date | Reviewer | Notes |
|---|---|---|
| | | |
