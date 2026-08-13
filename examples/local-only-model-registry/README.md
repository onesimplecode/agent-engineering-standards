# Worked Example: Fail-Loud Local-Only Model Verification (TR-SEC-003)

TR-SEC-003 says PII must be routed to local LLMs only. Stating that as policy
is not the same as enforcing it: a routing rule that lives only in a config
default, with no verification step, can drift to a cloud model silently --
the default gets overridden, a new task is added without updating the
routing doc, or the enforcement code itself exists but nothing calls it.
That last failure mode is not hypothetical: it is exactly what happened in
the project this pattern was extracted from, where a local-only enforcement
function was implemented and tested but never wired into either of the two
entry points that needed it, so it silently never ran while the design doc
read as satisfied.

## The pattern

| File | Role |
|---|---|
| `registry.py` | `MODEL_REGISTRY` (the single source of truth for provider family per model string) and `validate_local_only()` |

1. **Declare provider metadata once.** `MODEL_REGISTRY` maps each known model
   string to a `"local"` or `"cloud"` `ModelInfo`. Task-level config keeps
   storing plain model strings; the registry is the one place that knows
   what a given string actually resolves to.
2. **Verify at the one choke point every caller already passes through.**
   `validate_local_only()` is designed to be called from inside whatever
   single function already builds the running config for every entry point
   (a `load_config()`, a settings loader, an app factory) -- not duplicated
   into each entry point's own startup code. If two different call sites
   both need to remember to invoke the same check, one of them eventually
   won't.
3. **Fail loud on the unverifiable case, not just the known-bad case.** A
   model string with no `MODEL_REGISTRY` entry raises, the same as one that's
   registered but resolves to `"cloud"`. It is not assumed local by default.

## Why fail loud on "unregistered", not just "known cloud"

The tempting simpler version of this pattern only checks entries that are
*explicitly* known to be cloud, and lets anything else through. That's
weaker than it looks: the moment someone overrides a field to a new model
string that was never added to the registry, the check silently stops
protecting that field -- exactly the "control exists but doesn't actually
run for this case" shape TR-SEC-003 exists to prevent. Registering a model
before it can pass verification is the cost of keeping the check meaningful.

## The drift guard

`test_drift_guard_every_default_is_registered` (in
`tests/test_local_only_model_registry_example.py`) asserts every model this
project ships as a default has a `MODEL_REGISTRY` entry -- the same
"unreviewed grant" shape `scripts/agent-permission-guard.py` (TR-SEC-010)
and `examples/provenance-trust-tags/` guard against: adding a new default
model without deciding its provider family fails a test instead of silently
falling into the unregistered branch the first time someone enables
`require_local_only`.

## Applying this in a new project

1. Build `MODEL_REGISTRY` explicitly for every model string your config can
   resolve to -- resist a permissive "assume local unless proven cloud"
   default; the registry's *absence* of an entry, not an explicit `"cloud"`
   line, should trigger the fail-loud path.
2. Find the one function every entry point already calls to build its
   config, and call `validate_local_only()` at the end of it. If no such
   single function exists yet, that's worth creating before adding this
   check -- otherwise you're back to N call sites to keep in sync.
3. Gate the check behind an explicit flag (`require_local_only` here),
   defaulted off, so adopting this pattern is additive and doesn't change
   behavior for projects where nothing is PII-sensitive yet.
4. Add the drift-guard test before adding your second model default, not
   after.

## Honest limit

This verifies *configuration*, not *runtime behavior* -- it confirms the
model string a task is configured to call resolves to a local provider, not
that the actual HTTP call at runtime went where the config says it should
(a bug in the LLM client library itself, for instance, is out of scope
here). It is a config-time gate, not a network-egress monitor; pair it with
egress logging/allowlisting for the runtime guarantee.

## Trace to standards artifacts

| Artifact | Location |
|---|---|
| TR-SEC-003 definition | `registry/tr-registry.yaml` |
| Least-agency / unreviewed-grant drift-guard precedent | `AGENTS.md` -- "Guard Pattern: Co-located Reviewed Baselines", `scripts/agent-permission-guard.py` |
| Fail-closed classification precedent (same shape, different domain) | `examples/provenance-trust-tags/` (TR-SEC-011) |
