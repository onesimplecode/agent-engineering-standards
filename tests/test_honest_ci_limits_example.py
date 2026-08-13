"""Structural tests for examples/honest-ci-limits/ (v0.9 docs-first export).

These fixtures are documentation — assert the honest-limit language and
minimal shapes are present so the example cannot silently lose its point.
"""

from __future__ import annotations

from pathlib import Path

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "honest-ci-limits"


def test_readme_states_friction_not_barrier() -> None:
    text = (EXAMPLE / "README.md").read_text(encoding="utf-8").lower()
    assert "friction" in text
    assert "barrier" in text
    assert "branch protection" in text or "human review" in text


def test_ci_header_states_honest_limit_and_permissions() -> None:
    text = (EXAMPLE / "ci-header.example.yml").read_text(encoding="utf-8")
    assert "HONEST LIMIT" in text
    assert "permissions:" in text
    assert "contents: read" in text
    assert "What this example CI will NOT do" in text
    # SHA-pinned action style (full hash comment), not a floating major tag only
    assert "actions/checkout@" in text
    assert "# v" in text


def test_gitignore_example_has_negation_allowlist_and_honest_limit() -> None:
    text = (EXAMPLE / "gitignore.example").read_text(encoding="utf-8")
    assert "HONEST LIMIT" in text
    assert ".env" in text
    assert text.count("!") >= 1  # at least one negation allowlist entry
