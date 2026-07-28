# Worked Example: Spotlighting Drift Guard (TR-SEC-005)

Spotlighting delimits untrusted retrieved/external content so an LLM treats
it as data, not instructions — Microsoft's measurements put this at cutting
indirect prompt-injection success from >50% to <2%. The wording that
implements it (a security-notice string plus open/close delimiters) is
security-critical text: if a second LLM boundary pastes its own copy instead
of importing the single source, the two copies can silently drift apart.

| File | Role |
|---|---|
| `spotlighting_constants.py` | The single source — `SECURITY_NOTICE`, `UNTRUSTED_CONTENT_OPEN`, `UNTRUSTED_CONTENT_CLOSE`, and a `wrap_untrusted()` helper |
| `violation_example.py` | **Planted problem** — a second LLM boundary that pasted its own copy of the notice and delimiter text instead of importing it |

Run from the public repo root:

```bash
python3 scripts/spotlighting-drift-guard.py \
    --constants-file examples/spotlighting/spotlighting_constants.py \
    --scan-root examples/spotlighting
```

Expected output (exit code 1 — this fixture is *supposed* to fail):

```
DRIFT examples/spotlighting/violation_example.py: re-inlines the literal value of SECURITY_NOTICE (defined in examples/spotlighting/spotlighting_constants.py) instead of importing it
DRIFT examples/spotlighting/violation_example.py: re-inlines the literal value of UNTRUSTED_CONTENT_OPEN (defined in examples/spotlighting/spotlighting_constants.py) instead of importing it
DRIFT examples/spotlighting/violation_example.py: re-inlines the literal value of UNTRUSTED_CONTENT_CLOSE (defined in examples/spotlighting/spotlighting_constants.py) instead of importing it
```

The guard parses `spotlighting_constants.py` via Python's AST (not a
line-oriented regex), so `SECURITY_NOTICE`'s multi-line, implicitly
concatenated definition is compared as its true, full value — a copy that
matched only the first line would not be enough to escape detection.

`.github/workflows/spotlighting-drift-guard-demo.yml` runs this exact command
in CI on every change to this fixture or the script — the job's *success*
condition is that the drift is still caught, the same pattern as
`agent-permission-guard-demo.yml`.

**Honest limit** (see `templates/threat-model.md`'s Impossible vs. Tedious
section): this is a friction control against casual, undiscussed copy-paste
drift — it forces a second boundary to import the constant, or the diff fails
loud in review. It is not a barrier against a determined author who edits the
constants file and re-inlines a *modified* value that happens not to match
the old one; branch protection and human review of that diff are the real
backstop.
