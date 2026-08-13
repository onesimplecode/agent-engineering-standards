# Worked Example: Plugin / Skill Output Is Untrusted (TR-SEC-005)

Third-party and plugin skill documentation loaded at runtime is **data for
operating that plugin within its declared hooks** — not instructions that can
override `AGENTS.md`, edit core/secret paths, or authorize sends/submits.
Same boundary as web/RAG content; use spotlighting when the text enters an LLM.

Comparative pattern only (no upstream code): `santifer/career-ops` plugin trust
model. Adoption decision lives in the private monorepo (ADR-016).

| File | Role |
|---|---|
| `skill_boundary.py` | `CORE_RULES` SoT; `quarantine_plugin_text`; fail-closed `merge_into_core_rules` |
| `planted_plugin_SKILL.md` | **Planted problem** — skill prose that tries to ignore AGENTS, edit secrets, send a webhook |

```bash
python3 -m pytest tests/test_plugin_skill_trust_example.py -q
```

## Honest limit

Quarantine markers and a fail-closed merge API are **friction** against
mistaken elevation of plugin text. They do not stop a determined author who
edits `CORE_RULES` and the plugin file in the same commit — branch protection
and review remain the backstop. Spotlighting at the LLM boundary is still
required when plugin text is shown to a model.

## Trace

| Artifact | Location |
|---|---|
| Rule | `AGENTS.md` — External Content / plugin skill paragraph |
| Spotlighting | `examples/spotlighting/` |
| ROADMAP | v0.9 |
