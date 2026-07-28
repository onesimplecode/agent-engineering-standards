"""Tests the strict LLM output-schema validation reference implementation
(TR-SEC-012, v0.7 export) in examples/strict-output-schema/validate_llm_output.py.

Contract under test: parse_naive() demonstrates the fail-open bool("false")
coercion bug and accepts an unranged/string-coerced confidence; parse_strict()
rejects both instead of coercing, while still honoring "field absent" as a
distinct, valid default state.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

EXAMPLE_DIR = Path(__file__).resolve().parent.parent / "examples" / "strict-output-schema"
sys.path.insert(0, str(EXAMPLE_DIR))

from validate_llm_output import (  # noqa: E402
    SchemaValidationError,
    parse_naive,
    parse_strict,
)


def test_naive_parser_fails_open_on_string_false() -> None:
    # The bug this whole pattern exists to prevent: bool("false") is True.
    result = parse_naive({"relevant": "false", "confidence": 0.5})
    assert result.relevant is True  # documents the fail-open bug, not desired behavior


def test_naive_parser_accepts_unranged_confidence() -> None:
    result = parse_naive({"relevant": True, "confidence": 999})
    assert result.confidence == 999


def test_naive_parser_accepts_string_coerced_confidence() -> None:
    result = parse_naive({"relevant": True, "confidence": "0.9"})
    assert result.confidence == 0.9


def test_strict_parser_rejects_string_false_instead_of_coercing() -> None:
    with pytest.raises(SchemaValidationError, match="'relevant' must be a JSON boolean"):
        parse_strict({"relevant": "false", "confidence": 0.5})


def test_strict_parser_accepts_real_boolean() -> None:
    result = parse_strict({"relevant": False, "confidence": 0.5})
    assert result.relevant is False


def test_strict_parser_defaults_true_on_genuine_absence() -> None:
    result = parse_strict({"confidence": 0.5})
    assert result.relevant is True


def test_strict_parser_rejects_out_of_range_confidence() -> None:
    for bad in (999, -5, 1.01, -0.01):
        with pytest.raises(SchemaValidationError, match="out of range"):
            parse_strict({"relevant": True, "confidence": bad})


def test_strict_parser_rejects_string_confidence_instead_of_coercing() -> None:
    with pytest.raises(SchemaValidationError, match="'confidence' must be numeric"):
        parse_strict({"relevant": True, "confidence": "0.9"})


def test_strict_parser_rejects_boolean_confidence() -> None:
    with pytest.raises(SchemaValidationError, match="'confidence' must be numeric"):
        parse_strict({"relevant": True, "confidence": True})


def test_strict_parser_rejects_missing_confidence() -> None:
    with pytest.raises(SchemaValidationError, match="'confidence' must be numeric"):
        parse_strict({"relevant": True})
