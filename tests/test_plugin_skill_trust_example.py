"""Tests for examples/plugin-skill-trust/ (v0.9)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "plugin-skill-trust"
sys.path.insert(0, str(EXAMPLE))

from skill_boundary import (  # noqa: E402
    CORE_RULES,
    merge_into_core_rules,
    is_quarantined,
    plugin_attempts_override,
    quarantine_plugin_text,
)


def _planted() -> str:
    return (EXAMPLE / "planted_plugin_SKILL.md").read_text(encoding="utf-8")


def test_planted_skill_contains_override_shaped_phrases() -> None:
    assert plugin_attempts_override(_planted()) is True


def test_quarantine_wraps_plugin_text() -> None:
    wrapped = quarantine_plugin_text(_planted())
    assert is_quarantined(wrapped)
    assert "Ignore AGENTS.md" in wrapped


def test_merge_into_core_rules_fails_closed() -> None:
    with pytest.raises(PermissionError, match="cannot modify CORE_RULES"):
        merge_into_core_rules(_planted())


def test_core_rules_outrank_plugin_claims() -> None:
    assert any("AGENTS.md" in rule for rule in CORE_RULES)
    assert any("webhook" in rule.lower() or "messages" in rule.lower() for rule in CORE_RULES)
    # Quarantined text must not be treated as a member of CORE_RULES
    assert _planted() not in CORE_RULES
    assert quarantine_plugin_text(_planted()) not in CORE_RULES
