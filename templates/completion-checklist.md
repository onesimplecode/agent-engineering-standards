# Completion Checklist

Complete before marking any non-trivial implementation done. Attach to the
change summary or pull request description with evidence for each item.

## Checklist

- [ ] **Acceptance criteria coverage** — every acceptance criterion for this task
  has a specific file path and line number in the implementation cited here.

- [ ] **Test completeness** — all acceptance criteria, edge cases, and error
  scenarios have tests. Tests were written before or alongside the implementation
  (not after). No acceptance criterion is covered only by a mock that could mask
  a wrong signature.

- [ ] **Pattern adherence** — every new module, class, or function matches an
  existing codebase pattern, or an ADR explains why a new pattern is needed.
  Cite the reference file and line for each new structural choice.

- [ ] **First-party symbol verification** — every function, class, method, or
  type imported from another module in this repo has been grep-confirmed to
  exist at the cited path. No assumed or hallucinated signatures.

- [ ] **Data flow trace** — the end-to-end data flow for this change is traced
  explicitly: input schema → transformation → output schema at each boundary.
  Type compatibility is confirmed at every hand-off point.

- [ ] **Post-write verification** — persistent writes or external side effects
  have an observable verification step, not only a successful return value.

- [ ] **Ground-truth verification for agent security claims** — if this task
  verified an isolation, permission, or memory-scoping property of an agent,
  the evidence is a direct read of the enforcement point (an API, a database
  row, a log line), not the agent's own self-report in conversation. N/A if
  this task made no such claim.

- [ ] **Reviewer scope complete** — the reviewer prompt enumerated all changed
  artifact types: source files, test files, AND docs / ADRs / agent-instruction
  files. A review covering only code is incomplete when docs were also changed.

## Evidence

Fill in per item before committing:

| Item | Evidence (file:line or N/A with reason) |
|---|---|
| Acceptance criteria coverage | |
| Test completeness | |
| Pattern adherence | |
| First-party symbols | |
| Data flow trace | |
| Post-write verification | |
| Ground-truth verification for agent security claims | |
| Reviewer scope complete | |

## Gap Log

If any item has a gap: describe it, the fix applied, and re-verify.

| Gap found | Fix applied | Re-verified |
|---|---|---|
| | | |
