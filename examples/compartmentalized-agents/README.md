# Worked Example: Two-Layer Isolation for Multi-Agent Tool/Data Access (TR-SEC-013, TR-TEST-007)

Two agents sharing one backing service is a common shape: one has an
external input path (internet content, untrusted user messages), the other
holds broader privileges over the same data but no external egress. If
isolation between them lives in a single layer, a bug in that one layer is a
full compromise of the split.

## The pattern

Two independent layers, neither a substitute for the other:

1. **Tool-registry scope** (`ToolRegistry` in `isolation.py`) — what's
   *offered* to a given agent's own reasoning. Each agent (`identity`) gets
   its own credential and its own registered tool set; the server decides
   what a credential may invoke, not the agent's own restraint.
2. **Data-layer scope** (`DataStore`) — what's *reachable* even if layer 1
   has a bug. A per-identity role on the underlying data (here, `insert` /
   `select` permissions per table), enforced independently of whatever the
   tool registry believes it authorized.

The most-exposed agent (external input path) gets the narrowest grant at
both layers — typically insert-only into a quarantine table, no read-back
elsewhere. The most broadly-privileged agent gets no external egress at all.

## Why two layers, not one

`test_data_layer_still_blocks_when_tool_layer_is_misconfigured` (in
`tests/test_compartmentalized_agents_example.py`) simulates the exact bug
class this pattern defends against: a tool-registry entry wrongly registers
one identity with a tool that mutates data it should never reach. The tool
layer's bug does not matter — the data-layer role rejects the call anyway.
A single-layer design (tool scoping alone, or data roles alone) would not
survive this test: tool scoping alone has nothing left to stop the call once
it's wrongly registered; data roles alone never restricted what was *offered*
to the compromised or over-broad tool call in the first place.

## Verifying isolation directly, not by asking the agent (TR-TEST-007)

`ToolRegistry.list_tools(identity)` and `DataStore.select(identity, table)`
are called directly in the tests to assert what each identity can actually
reach. A property like "can agent B see agent A's tools" should be verified
against the registry/store's own state — not inferred from asking an agent
in conversation whether it has access to something.

`SelfReportingAgent` (`isolation.py`) makes this concrete: its
`claims_to_have_tool(...)` answer comes from a snapshot decoupled from the
registry — an onboarding-time belief, a stale cache, a question answered by
the wrong backend — the same way an agent's chat answer to "do you have tool
X" is decoupled from whatever actually enforces access.
`test_self_report_can_give_a_false_pass_ground_truth_catches_it` shows the
failure mode directly: `curator`'s self-report denies having a tool it was
actually (wrongly) granted — looks isolated, isn't. Trusting the self-report
alone would have signed off on a real leak; only
`ToolRegistry.list_tools("curator")`, the actual enforcement point, reveals
it. This is why a security-property claim about an agent needs ground-truth
verification, not a chat transcript, as its evidence.

## Applying this in a new project

1. Model each agent as its own `identity` string (or credential) from the
   start — never a shared key across agents that differ in trust level.
2. Register tools per identity explicitly; resist a default/wildcard
   registration that "just works" for every identity.
3. Grant data-layer permissions per identity, scoped to exactly the
   operations that agent's role requires (e.g. insert-only for a
   quarantine/inbox table).
4. Write a test that deliberately misconfigures layer 1 (register a tool
   that shouldn't exist for that identity) and asserts layer 2 still blocks
   the resulting data operation — this is the test that actually proves
   defense in depth, not just that both layers exist.
5. When verifying any isolation/permission claim about a real agent, query
   the enforcement point's own API, database, or logs directly — never rely
   on the agent's own answer in conversation as the evidence, even when that
   answer happens to sound reassuring.

## Honest limit

This example models the isolation *shape* — it is not a working MCP server
or a real database role system. A production implementation still needs the
underlying transport (MCP, gRPC, REST) to correctly attribute each call to
the right identity/credential, and the underlying data store to actually
enforce roles at the connection level, not just in application code sitting
in front of a shared superuser connection.

## Trace to standards artifacts

| Artifact | Location |
|---|---|
| TR-SEC-013 definition | `registry/tr-registry.yaml` |
| TR-TEST-007 definition | `registry/tr-registry.yaml` |
| Compartmentalized isolation rule | `AGENTS.md` — "Compartmentalized Multi-Agent Isolation" |
| Ground-truth verification rule | `AGENTS.md` — "Ground-Truth Verification for Agent Security Claims" |
| Least-agency precedent this extends | `AGENTS.md` — "Threat Modeling and Least Agency (TR-SEC-008/009/010)" |
| Completion-checklist gate | `templates/completion-checklist.md` |
