# Named-agent authority manifests

This reference implements **TR-AGT-012**: a declared named agent must have an explicit, non-empty
tool allowlist. An absent named-agent block selects a deliberately unnamed legacy surface; an empty
or malformed declared block is an error, never shorthand for every tool.

`manifest.py` takes an already-parsed configuration mapping so it has no dependency beyond Python's
standard library. Call `parse_named_agents()` during application configuration loading, before any
endpoint is registered. Then call `build_named_registries()` with the live registered tool mapping;
it rejects unknown names and builds a separate dictionary for each identity.

The companion tests demonstrate the intended proof obligations:

- omitted named mode remains distinct compatibility behavior;
- explicit `null`, empty mappings, omitted `tools`, empty lists, and blank names fail before startup;
- endpoint names use a transport-safe lowercase route grammar, so path-like or padded identities
  cannot desynchronize routing and authorization;
- an endpoint contains only its declared tools; and
- a declaration for a tool absent from the live registry fails before endpoint construction.

This pattern governs standing tool authority. It does not authorize per-item data egress: use an
owner-controlled approval mechanism for that separate problem.
