"""Reference implementation: strict LLM output-schema validation (TR-SEC-012).

Every field a model returns gets a type check AND a range/shape check.
Reject on mismatch -- never coerce. Both a naive and a strict parser are
shown for the same schema (a generic relevance-classifier response: a
boolean "relevant" field and a numeric "confidence" field in [0.0, 1.0]) so
the failure mode is directly comparable.
"""

from __future__ import annotations

from dataclasses import dataclass


class SchemaValidationError(ValueError):
    """Raised by the strict parser -- treat as a possible injection/malformed
    response and retry, never silently substitute a default."""


@dataclass
class ClassificationResult:
    relevant: bool
    confidence: float


def parse_naive(response: dict) -> ClassificationResult:
    """Anti-pattern: coerces instead of validating.

    bool(x) is True for ANY non-empty string, including the JSON string
    "false" -- a model (or an injected instruction inside the content being
    classified) that returns {"relevant": "false"} silently flips to
    relevant=True here. confidence is accepted unranged: 999 or -5 both pass.
    """
    return ClassificationResult(
        relevant=bool(response.get("relevant", True)),
        confidence=float(response.get("confidence", 0.0)),
    )


def parse_strict(response: dict) -> ClassificationResult:
    """Type AND range checks; reject, never coerce.

    Absence of "relevant" is a defined, valid state (defaults True, matching
    a documented fail-open relevance-gate posture for genuine absence only).
    A *present* field of the wrong type is a different state entirely and
    must not share that fallback -- it raises.
    """
    if "relevant" in response and response["relevant"] is not None:
        relevant = response["relevant"]
        if not isinstance(relevant, bool):
            raise SchemaValidationError(
                f"'relevant' must be a JSON boolean, got {type(relevant).__name__}: "
                f"{relevant!r} -- possible injection attempt"
            )
    else:
        relevant = True  # documented default for genuine absence, not for wrong-type

    confidence = response.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        raise SchemaValidationError(
            f"'confidence' must be numeric, got {type(confidence).__name__}: {confidence!r}"
        )
    if not (0.0 <= confidence <= 1.0):
        raise SchemaValidationError(
            f"'confidence' out of range [0.0, 1.0]: {confidence!r} -- possible injection attempt"
        )

    return ClassificationResult(relevant=relevant, confidence=confidence)
