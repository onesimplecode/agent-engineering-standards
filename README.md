# LumiaForge AI Engineering Standards

An auditable **engineering operating model** for agent-assisted software work — not another
prompt library or RAG platform.

## Problem

AI coding agents default to the shortest path: skip tests, leak context across trust boundaries,
drift config and docs, and loop without budgets. Senior engineers prevent these failures with
standards, reviews, and deterministic checks. This repository packages that discipline for
public reuse.

## What this is

| Included | Not included |
|----------|----------------|
| Machine-readable requirement registry (`registry/tr-registry.yaml`) | Production runtime or hosted services |
| Portable agent conventions (`AGENTS.md`, `agents/`) | Tool-specific private agent sessions |
| Governance and eval templates (ADR, impact assessment, maturity checklist, LLM eval, completion checklist) | Full application frameworks |
| Reference scripts (config drift, debt tags, release validation, Cursor rule export, llms.txt manifest, agent permission guard, spotlighting drift guard) | Full `agent-skills` replacement |
| Synthetic worked example | Personal data |

## Quick start

```bash
# Validate a staging tree (or this repo root)
python3 scripts/public-export-check.py .

# Scan for config/model-string drift (point at your app monorepo)
python3 scripts/check-config-consistency.py --root /path/to/your/repo --app YourApp

# Report deferred-work tags
python3 scripts/debt-report.py --path /path/to/your/repo

# Export the registry as Cursor project rules (see examples/cursor-rules/)
python3 scripts/cursor-rules-adapter.py --out /path/to/your/repo/.cursor/rules

# Regenerate this repo's own llms.txt cross-tool discovery manifest
python3 scripts/llms-txt-generator.py

# Check an agent settings file's tool-permission grants against a reviewed baseline
python3 scripts/agent-permission-guard.py --settings /path/to/your/settings.json

# Check that spotlighting security-notice/delimiter constants aren't re-inlined elsewhere
python3 scripts/spotlighting-drift-guard.py --constants-file /path/to/your/constants.py --scan-root /path/to/your/src
```

## Adopting this into your project

A step-by-step path for pulling these standards into your own repo, not just this one:

1. **Read the model** — [`docs/ai-engineering-operating-model.md`](docs/ai-engineering-operating-model.md)
   explains the four layers (requirements, roles, artifacts, checks) and the
   failure modes they guard against.
2. **Pull in agent conventions** — copy or reference [`AGENTS.md`](AGENTS.md) and
   the role specs in [`agents/`](agents/) into your own repo so any AI coding
   tool reads the same rules.
3. **Run the checks against your repo** — point the Quick start scripts above at
   your own monorepo (`--root /path/to/your/repo`) instead of this one.
4. **Adopt templates as needed** — the ADR, impact assessment, maturity
   checklist, LLM eval, and completion checklist templates in
   [`templates/`](templates/) are meant to be copied, not just read.
5. **Study the worked traces** — [`examples/worked-example/`](examples/worked-example/),
   [`examples/agent-permission-guard/`](examples/agent-permission-guard/),
   [`examples/spotlighting/`](examples/spotlighting/),
   [`examples/provenance-trust-tags/`](examples/provenance-trust-tags/),
   [`examples/strict-output-schema/`](examples/strict-output-schema/), and
   [`examples/compartmentalized-agents/`](examples/compartmentalized-agents/) show
   a requirement moving end-to-end: TR-ID → ADR → maturity row → script → CI gate.
6. **Reconcile with tools you already use** — [`docs/agent-skills-integration.md`](docs/agent-skills-integration.md)
   covers how this layers under AGENTS.md, agent-skills, and Cursor rules rather
   than replacing them.

None of this requires forking the repo — steps 2–4 are copy-in, and every
script in step 3 takes a root-path argument (`--root`, `--path`, `--out`,
`--settings`, or a positional path, depending on the script — see each
command's `--help`) precisely so it can target your own repo instead of this
one.

## Enforced workflow

See [`examples/worked-example/`](examples/worked-example/) for a synthetic trace:

**TR-AGT-004** → ADR → maturity checklist row → `LUMIA-DEBT:` tag → `check-config-consistency.py`

See [`examples/agent-permission-guard/`](examples/agent-permission-guard/) for the
security guardrail trace (TR-SEC-010): a planted wildcard grant and an
unreviewed grant, both caught by `scripts/agent-permission-guard.py`'s
co-located reviewed baseline — the "make dangerous changes loud, not
impossible" pattern.

See [`examples/spotlighting/`](examples/spotlighting/) for the untrusted-content
delimiting trace (TR-SEC-005): a planted re-inlined copy of the
security-notice/delimiter constants, caught by
`scripts/spotlighting-drift-guard.py`'s single-source enforcement.

See [`examples/provenance-trust-tags/`](examples/provenance-trust-tags/) (TR-SEC-011)
for the fail-closed content-trust derivation pattern — a drift-guarded mapping
from source type to trust level — and
[`examples/strict-output-schema/`](examples/strict-output-schema/) (TR-SEC-012) for
a live repro of the `bool("false") is True` fail-open coercion bug and the
reject-never-coerce fix.

See [`examples/compartmentalized-agents/`](examples/compartmentalized-agents/)
for the two-layer multi-agent isolation trace (TR-SEC-013) — a simulated
tool-registry misconfiguration that a per-agent data-layer role alone still
blocks — and the ground-truth-vs-self-report trace (TR-TEST-007): an agent's
own claim about its tool access shown giving a false pass that only the tool
registry's actual state catches.

## Public Evidence Map

- [`AGENTS.md`](AGENTS.md) — tool-neutral agent rules for data routing, loop contracts,
  trigger classification, external-content trust boundaries, and deterministic checks.
- [`agents/`](agents/) — reusable role specs for developer, reviewer, private researcher,
  and public researcher agents.
- [`docs/ai-engineering-operating-model.md`](docs/ai-engineering-operating-model.md) —
  the overall model: requirements, roles, artifacts, checks.
- [`docs/requirements-implementation-map.md`](docs/requirements-implementation-map.md) —
  where each public requirement is implemented and how strongly it is enforced.
- [`templates/llm-eval.md`](templates/llm-eval.md) and
  [`templates/completion-checklist.md`](templates/completion-checklist.md) —
  eval and self-critique patterns that make agent output reviewable.
- [`llms.txt`](llms.txt) — generated, drift-gated cross-tool discovery manifest
  (registry + agent roles + templates + scripts) following the emerging
  llms.txt convention (https://llmstxt.org); regenerate with
  `scripts/llms-txt-generator.py`. Generated at this repo's own root only —
  unlike the Cursor adapter, there's no `examples/llms-txt/` export target,
  since this manifest describes this repo, not a repo you'd point it at.

## Positioning

- **Complements** [AGENTS.md](https://agents.md), [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills), and runtime governance tools —
  see [`docs/agent-skills-integration.md`](docs/agent-skills-integration.md) for the layer split and integration patterns.
- **Differentiator:** design-time traceability — requirement IDs, PII routing rules, loop contracts,
  trigger classification, and scriptable drift detection.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Releases follow [ROADMAP.md](ROADMAP.md) and [CHANGELOG.md](CHANGELOG.md).

## License

MIT — see [LICENSE](LICENSE). Third-party influences: [ATTRIBUTIONS.md](ATTRIBUTIONS.md).
