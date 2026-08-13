"""Tests for examples/thin-pointer/ (v0.9 minimal export)."""

from __future__ import annotations

from pathlib import Path

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "thin-pointer"
CANONICAL = EXAMPLE / "canonical" / "review-checklist.md"
AGENTS_WRAPPER = EXAMPLE / "wrappers" / "AGENTS.snippet.md"
CURSOR_WRAPPER = EXAMPLE / "wrappers" / "cursor-rule.snippet.mdc"
CANONICAL_REL = "examples/thin-pointer/canonical/review-checklist.md"


def test_canonical_has_full_steps() -> None:
    text = CANONICAL.read_text(encoding="utf-8")
    assert "single source of truth" in text.lower() or "only** full copy" in text.lower()
    # At least several numbered steps live only here
    assert text.count("\n1.") + text.count("\n2.") >= 2


def test_wrappers_point_at_canonical_and_stay_short() -> None:
    for wrapper in (AGENTS_WRAPPER, CURSOR_WRAPPER):
        text = wrapper.read_text(encoding="utf-8")
        assert CANONICAL_REL in text
        # Thin: wrappers must not re-host the numbered checklist body
        assert "Verify secrets and PII" not in text
        assert len(text.splitlines()) < 40


def test_wrappers_are_shorter_than_canonical() -> None:
    canon_len = len(CANONICAL.read_text(encoding="utf-8"))
    assert len(AGENTS_WRAPPER.read_text(encoding="utf-8")) < canon_len
    assert len(CURSOR_WRAPPER.read_text(encoding="utf-8")) < canon_len
