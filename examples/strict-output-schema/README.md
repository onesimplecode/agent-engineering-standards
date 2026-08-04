# Worked Example: Strict LLM Output-Schema Validation (TR-SEC-012)

Every field a model returns needs a type check **and** a range/shape check.
Reject on mismatch — never coerce. `validate_llm_output.py` shows the same
schema parsed two ways so the failure mode is directly comparable.

## The bug this guards against

```python
>>> bool("false")
True
```

Any non-empty string is truthy in Python. A parser that does
`bool(response.get("relevant", True))` on a model's JSON response silently
flips the JSON **string** `"false"` to `True` — exactly backwards, and fails
open through whatever gate `relevant` controls. `test_naive_parser_fails_open_on_string_false`
in `tests/test_strict_output_schema_example.py` reproduces this live against
`parse_naive()`.

The same naive parser also accepts an unranged `confidence`: `999` or `-5`
both pass a bare `float(...)` cast, and so does the **string** `"0.9"` (which
`float()` happily coerces) — silently defeating any downstream range check
that assumes `confidence` is already a validated number.

## The fix

`parse_strict()`:

| Field | Naive (`parse_naive`) | Strict (`parse_strict`) |
|---|---|---|
| `relevant` | `bool(x)` — any truthy value passes, including the string `"false"` | Must be a real JSON boolean when present; wrong type raises `SchemaValidationError` |
| `relevant` absent | Defaults `True` | Still defaults `True` — absence is a defined valid state, distinct from wrong-type |
| `confidence` | `float(x)` — unranged, coerces strings | Must be numeric (not `bool`, not `str`) **and** in `[0.0, 1.0]`; either failure raises |

Absence and wrong-type are **not** the same state and must not share a
fallback path: a model that omits `relevant` is using a documented,
intentional default; a model (or an injected instruction) that returns
`relevant: "false"` as a string is malformed input that should fail the call
and consume a retry, not silently coerce to the opposite of what it said.

## Pairs with single-source-of-truth (TR-GOV-001)

A strict parser for a given output schema is defined once and imported by
every caller of that LLM boundary — the same convention this repo already
documents for model names, endpoints, and thresholds (`AGENTS.md` — "Single
Source of Truth").

## Applying this in a new project

1. For every LLM call whose output drives a decision (a gate, a threshold, a
   boolean routing choice), write one strict parser function for that
   response schema.
2. Type-check with `isinstance`, not duck-typing coercion (`bool()`,
   `float()`, `int()` on unknown input).
3. Range/shape-check numeric and enum-like fields explicitly.
4. Raise on any mismatch — let the caller's existing retry logic handle it,
   the same way a network timeout would be retried.
5. Keep "field absent" and "field present but wrong type" as explicitly
   distinct branches; only the former should have a soft default.

## Honest limit

This validates *shape*, not *meaning* — a strictly well-typed `confidence:
0.95` can still be wrong if the model reasoned poorly. Schema validation
closes the coercion-based fail-open class of bug; it is not a substitute for
eval-driven quality measurement of the model's actual judgment.

## Trace to standards artifacts

| Artifact | Location |
|---|---|
| TR-SEC-012 definition | `registry/tr-registry.yaml` |
| Strict output-schema rule | `AGENTS.md` — "Strict LLM Output-Schema Validation" |
| Single-source-of-truth convention this pairs with | `AGENTS.md` — "Single Source of Truth (TR-GOV-001)" |
