# Worked Example: TR-AGT-004 End-to-End (Synthetic)

This directory shows how one requirement flows through the governance
artifacts. **All content is fictional** — no private data or real application code.

## Trace

| Step | Artifact | Evidence |
|------|----------|----------|
| 1 | `registry-snippet.yaml` | TR-AGT-004 defined as active |
| 2 | `docs/decisions/ADR-001-example.md` | Trigger type classified: user-initiated |
| 3 | `docs/maturity-checklist.md` | A.9 human oversight row = Partial (trigger classified, no further action needed at POC) |
| 4 | `sample-app/CLAUDE.md` | Documents trigger classification |
| 5 | `check-config-consistency.py` | Real output below — catches the planted `local-gemma-model` drift (TR-GOV-001) |
| 6 | `.github/workflows/config-drift-demo.yml` | CI gate: fails the job if the drift is ever *not* detected (see `docs/maturity-checklist.md` A.10) |

## Run (from public repo root)

```bash
python3 scripts/public-export-check.py .
python3 scripts/debt-report.py --path examples/worked-example
python3 scripts/check-config-consistency.py --root examples/worked-example
```

## Deliberate drift example

`sample-app/CLAUDE.md` references `gemma4:31b` while `config/search_config.yaml.example`
uses `gemma4:26b`. Real output from the command above:

```
sample-app:
  DRIFT    local-gemma-model: 2 distinct values found
             'gemma4:31b' <- sample-app/CLAUDE.md:8
             'gemma4:26b' <- sample-app/config/search_config.yaml.example:5

See TR-GOV-001 (registry/tr-registry.yaml) for the convention this enforces.
```

(exit code 1). `.github/workflows/config-drift-demo.yml` runs this exact command in CI
on every change to this example or the script — the job's *success* condition is that
the drift is still caught. If a future change to the fixture or the detector makes this
pass clean, the job fails loudly instead of silently losing the example's teaching value.
