"""Tests for the TR-AGT-012 named-agent authority-manifest example."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


EXAMPLE_DIR = Path(__file__).resolve().parent.parent / "examples" / "named-agent-authority-manifest"
sys.path.insert(0, str(EXAMPLE_DIR))

from manifest import AuthorityManifestError, build_named_registries, parse_named_agents  # noqa: E402


def test_omitting_named_agents_selects_legacy_mode() -> None:
    assert parse_named_agents({"api": {}}) is None


@pytest.mark.parametrize(
    "config",
    [
        {"api": {"agents": None}},
        {"api": {"agents": {}}},
        {"api": {"agents": {"reviewer": {}}}},
        {"api": {"agents": {"reviewer": {"tools": []}}}},
        {"api": {"agents": {"reviewer": {"tools": ["read_note", ""]}}}},
    ],
)
def test_declared_named_manifests_fail_closed(config: dict[str, object]) -> None:
    with pytest.raises(AuthorityManifestError):
        parse_named_agents(config)


@pytest.mark.parametrize("name", ["", " reviewer", "reviewer ", "../admin", "a/b", "-leading"])
def test_route_unsafe_agent_identity_fails_before_endpoint_build(name: str) -> None:
    with pytest.raises(AuthorityManifestError, match="transport-safe"):
        parse_named_agents({"api": {"agents": {name: {"tools": ["read_note"]}}}})


def test_mixed_type_agent_identity_raises_manifest_error_not_type_error() -> None:
    with pytest.raises(AuthorityManifestError, match="transport-safe"):
        parse_named_agents(
            {"api": {"agents": {"reviewer": {"tools": ["read_note"]}, 1: {"tools": ["x"]}}}}
        )


def test_named_registry_contains_only_declared_tools() -> None:
    registries = build_named_registries(
        {"api": {"agents": {"reviewer": {"tools": ["read_note"]}}}},
        {"read_note": object(), "ingest_note": object()},
    )

    assert set(registries["reviewer"]) == {"read_note"}
    assert "ingest_note" not in registries["reviewer"]


def test_unknown_declared_tool_fails_before_endpoint_build() -> None:
    with pytest.raises(AuthorityManifestError, match="unknown tool"):
        build_named_registries(
            {"api": {"agents": {"reviewer": {"tools": ["delete_note"]}}}},
            {"read_note": object()},
        )
