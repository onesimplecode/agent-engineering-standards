# Worked Example: Fail-Closed Provenance Trust Tags (TR-SEC-011)

Agentic memory and RAG indexes are a poisoning surface: content ingested from
outside the system's own trust boundary sits in the same store the retriever
treats as authoritative. Without provenance tracking, a malicious instruction
embedded in an ingested web page is indistinguishable from the system
owner's own authored content at synthesis time.

## The pattern

Three layers, all deterministic — no LLM in the trust path:

1. **Tag at ingest.** Every ingested item records its `source_type` — a
   fact, not a judgment — at write time.
2. **Derive trust fail-closed, at read time, in code.** `trust.py`'s
   `SOURCE_TRUST_MAP` is the single source of truth. Only content types
   explicitly authored by the system's own owner earn the trusted tier;
   everything else — including a future `ContentType` member nobody has
   classified yet — resolves to `"untrusted"` through the map's fail-closed
   default. A row whose `source_type` was never recorded resolves to
   `"unverified"`, not silently trusted.
3. **Validate at retrieval, not only storage.** `trust_level_for()` is
   called per retrieved item at query time, so legacy/unclassified rows are
   caught on every read, not just flagged once at ingest and forgotten.

Deriving `trust_level` at read time instead of storing it means a future
mapping revision (reclassifying a source type) is a code change reviewed in
a PR, not a data migration.

## The drift guard

`test_drift_guard_every_content_type_is_classified` (in
`tests/test_provenance_trust_tags_example.py`) asserts every `ContentType`
member has an explicit entry in `SOURCE_TRUST_MAP` — the same "unreviewed
grant" shape as `scripts/agent-permission-guard.py` (TR-SEC-010): adding a
new content type without deciding its trust classification fails the test
instead of silently inheriting a default nobody chose on purpose.

## Quarantine, not trust-by-default

`is_quarantined()` marks `"untrusted"` and `"unverified"` content for
spotlighting (TR-SEC-005, see `examples/spotlighting/`) at the reasoning
boundary — wrapped in delimiters, never treated as instructions, regardless
of how confidently worded it is.

## Applying this in a new project

1. Define your own `ContentType` enum covering every source your ingest
   pipeline accepts.
2. Build `SOURCE_TRUST_MAP` explicitly — resist a permissive default; the
   map's *absence* of an entry, not an explicit `"untrusted"` line, is what
   should trigger the fail-closed fallback.
3. Call `trust_level_for()` at retrieval, not just at ingest, so content
   ingested before the mapping existed is still classified correctly today.
4. Route anything `is_quarantined()` flags through your spotlighting layer
   before it reaches an LLM prompt.

## Honest limit

This is provenance-based classification, not content inspection — it tells
you *where* content came from, not whether a specific chunk is safe. A
malicious instruction inside a `"trusted"`-sourced item (e.g. a compromised
user account) is not caught by this layer; defense in depth still requires
sanitization at ingest and spotlighting at the reasoning boundary regardless
of trust level.

## Trace to standards artifacts

| Artifact | Location |
|---|---|
| TR-SEC-011 definition | `registry/tr-registry.yaml` |
| Memory/provenance hygiene rule | `AGENTS.md` — "Memory / Provenance Hygiene" |
| Spotlighting (what quarantined content flows into) | `AGENTS.md`, `examples/spotlighting/` |
| Least-agency drift-guard precedent | `AGENTS.md` — "Guard Pattern: Co-located Reviewed Baselines", `scripts/agent-permission-guard.py` |
