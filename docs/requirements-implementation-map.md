# Requirements Implementation Map

This map shows how these public standards turn requirements into
concrete artifacts. It is intentionally limited to public, reusable evidence.

| Requirement area | Public implementation | Enforcement level | Evidence |
|---|---|---|---|
| Stable requirement IDs | Machine-readable registry | Documented + reusable | `registry/tr-registry.yaml` |
| Agent role boundaries | Tool-neutral role specs | Documented | `AGENTS.md`, `agents/*.md` |
| Private/public data routing | Role split and routing rule | Documented + reviewable | `AGENTS.md`, `agents/private-researcher.md`, `agents/public-researcher.md` |
| Local-only model verification | Config-driven provider registry + fail-loud check at the single config-build choke point; unregistered models rejected, not assumed local | Documented + registry + example | `registry/tr-registry.yaml` (TR-SEC-003), `examples/local-only-model-registry/` |
| Loop contracts | Required four-field node contract + earned MCP annotations + reference implementation | Documented + example | `AGENTS.md`, `registry/tr-registry.yaml` (TR-AGT-003), `examples/engine-interface/` |
| Deterministic post-processing | Structure/indexes/metadata/links owned by deterministic code, not agent tools | Documented + registry | `AGENTS.md`, `registry/tr-registry.yaml` (TR-AGT-006) |
| Self-healing metadata | Repair missing fields and flag inventions with an enrichment marker | Documented + registry | `AGENTS.md`, `registry/tr-registry.yaml` (TR-AGT-007) |
| Capability split by determinism | Four-tier taxonomy + deciding test (forget → judgment call) | Documented + registry | `AGENTS.md`, `registry/tr-registry.yaml` (TR-AGT-008) |
| Hooks vs schedules | Cheap deterministic on events; expensive LLM on schedules | Documented + registry | `AGENTS.md`, `registry/tr-registry.yaml` (TR-AGT-009) |
| Named agent authority manifests | Declared named endpoints have explicit non-empty tool allowlists; loader rejects omission/emptiness and endpoint construction scopes each registry | Documented + tested example | `AGENTS.md`, `registry/tr-registry.yaml` (TR-AGT-012), `examples/named-agent-authority-manifest/` |
| Knowledge confidence labels | Five-label claim vocabulary; contested never resolved by recency alone | Template | `templates/knowledge-confidence.md` |
| Trigger classification | ADR-triggered trigger type | Documented + example | `examples/worked-example/`, `templates/adr.md` |
| Behavioral mode declaration | Named, trigger-activated mode contract orthogonal to gate strictness | Documented | `AGENTS.md`, `registry/tr-registry.yaml` |
| External content trust boundary (spotlighting) | Retrieved content treated as data; single-sourced security-notice + delimiter constants with a CI drift guard that fails on any re-inlined copy | Documented + script + example | `AGENTS.md`, `registry/tr-registry.yaml`, `scripts/spotlighting-drift-guard.py`, `examples/spotlighting/`, `.github/workflows/spotlighting-drift-guard-demo.yml` |
| Memory/provenance hygiene | Source-tag at ingest, fail-closed trust derivation at read time, validated at retrieval, unverified/external content quarantined | Documented + registry + example | `AGENTS.md`, `registry/tr-registry.yaml` (TR-SEC-011), `examples/provenance-trust-tags/` |
| Strict LLM output-schema validation | Type and range checks on every model-returned field; reject, never coerce | Documented + registry + example | `AGENTS.md`, `registry/tr-registry.yaml` (TR-SEC-012), `examples/strict-output-schema/` |
| Compartmentalized multi-agent isolation | Two independent layers (tool-registry scope + data-layer scope) for agents sharing one backing service; a test proves layer 2 blocks a simulated layer-1 misconfiguration | Documented + registry + example | `AGENTS.md`, `registry/tr-registry.yaml` (TR-SEC-013), `examples/compartmentalized-agents/` |
| Credential-isolated broker operations | Scope- and revision-bound broker operations with single-use mutation leases and restart-safe read-only transport | Documented + registry + example | `AGENTS.md`, `registry/tr-registry.yaml` (TR-SEC-014), `examples/credential-isolated-broker/` |
| Ground-truth verification for agent security claims | An agent's self-report is not verification evidence for an isolation/permission/memory-scoping claim; verify against the enforcement point's own state | Documented + registry + template + example | `AGENTS.md`, `registry/tr-registry.yaml` (TR-TEST-007), `templates/completion-checklist.md`, `examples/compartmentalized-agents/` |
| Rollout sequencing (layering rule) | Foundational/shared infrastructure ships first; every later phase immediately usable on arrival, no phase idling behind an unmet dependency | Documented | `docs/ai-engineering-operating-model.md` |
| Design-time threat modeling | Trust boundaries, data classification, and ATT&CK/ATLAS technique mapping required for new listeners/credentials/tool grants/content sources | Template + example | `templates/threat-model.md`, `examples/worked-example/docs/decisions/ADR-004-example.md` |
| Impossible vs. tedious control classification | Every threat-model mitigation classified barrier vs. friction, with a named backstop for friction controls | Documented + template | `AGENTS.md`, `templates/threat-model.md` |
| Least agency / agent permission grants | No wildcard write/install/exec/network grants in agent allowlists | Documented | `AGENTS.md`, `registry/tr-registry.yaml` |
| Co-located reviewed-baseline guard pattern | Hard-coded baseline lives in the enforcing script itself, forcing the widening diff into the same PR | Documented + script + example | `AGENTS.md`, `scripts/agent-permission-guard.py`, `examples/agent-permission-guard/`, `.github/workflows/agent-permission-guard-demo.yml` |
| Honest CI limits (friction, not barriers) | Workflow headers, gitignore negation allowlists, and AGENTS prose state that repo-local CI guards are friction; branch protection + human review remain the backstop | Documented + example | `AGENTS.md`, `examples/honest-ci-limits/` |
| Outbound fetch hygiene (SSRF allowlist + hop re-check) | Host allowlist, fail-closed addresses, DNS pin, re-validate every redirect; socket/IP pin residual named honestly | Documented + example | `AGENTS.md`, `examples/ssrf-allowlist/` |
| Thin-pointer multi-runtime instructions | One canonical instruction tree; short harness wrappers point at it instead of forking prose | Documented + example | `AGENTS.md`, `docs/agent-skills-integration.md`, `examples/thin-pointer/` |
| Plugin / skill output untrusted (TR-SEC-005) | Third-party skill markdown quarantined as data; cannot merge into core rules or authorize sends/edits | Documented + example | `AGENTS.md`, `examples/plugin-skill-trust/` |
| CI least-privilege and SHA pinning | Explicit `permissions:` block per workflow; third-party actions pinned to a full commit SHA | Documented + CI | `registry/tr-registry.yaml`, `.github/workflows/*.yml` |
| LLM eval convention | Co-located golden eval files guarded by `LLM_EVAL=true` | Template | `templates/llm-eval.md`, `AGENTS.md` |
| Post-write verification | Persistent side effects require observable verification | Template + documented | `templates/completion-checklist.md`, `AGENTS.md` |
| Provider prompt portability | Provider-specific system prompt variants isolated from business logic | Documented | `AGENTS.md` |
| Completion self-critique | Acceptance coverage, tests, symbol verification, data flow, and verification; reviewer spot-checks cited file:line evidence against the diff | Template + role contract | `templates/completion-checklist.md`, `agents/reviewer.md` |
| ADR discipline | Standard decision template; deferred work names meantime degradation | Template | `templates/adr.md` |
| AI impact assessment | Affected parties, data, harms, mitigations | Template | `templates/ai-impact-assessment.md` |
| Maturity tracking | Per-app checklist pattern | Template | `templates/maturity-checklist.md` |
| Governance review cadence | Review cycle template | Template | `templates/governance-review.md` |
| Model/config drift | Deterministic scanner | Script | `scripts/check-config-consistency.py` |
| Cross-tool rule export | Cursor rules generated from the registry, drift-gated | Script + CI | `scripts/cursor-rules-adapter.py`, `examples/cursor-rules/`, `.github/workflows/release-check.yml` |
| Cross-tool discovery manifest | `llms.txt` generated from the registry, agent roles, templates, and scripts, drift-gated | Script + CI | `scripts/llms-txt-generator.py`, `llms.txt`, `.github/workflows/release-check.yml` |
| Deferred work visibility | Structured debt tags | Script | `scripts/debt-report.py` |
| Public release hygiene | Required docs, secret-like strings, artifact paths | Script + CI | `scripts/public-export-check.py`, `.github/workflows/release-check.yml` |
| Public support boundary | Contribution and issue policy | Documented | `CONTRIBUTING.md`, `SECURITY.md`, `.github/` |
| License/attribution boundary | License and influence disclosure | Documented | `LICENSE`, `ATTRIBUTIONS.md` |

## Status Categories

- **Documented** — human/agent instructions exist.
- **Template** — reusable artifact shape exists.
- **Script** — deterministic check exists.
- **CI** — check runs automatically in the public repo.

## Gaps By Design

This public repo does not include application source code, live production
metrics, or full deployment evidence. It shows the engineering operating
model and the checks that make it reusable.

## Recommended Review Path

1. Read `AGENTS.md` to understand the agent rules.
2. Read `registry/tr-registry.yaml` to see the stable requirement IDs.
3. Open `examples/worked-example/` to see one requirement flow through an ADR,
   maturity checklist, and drift-check example.
4. Run `python3 scripts/public-export-check.py .`.
