"""Tests the two-layer multi-agent isolation reference implementation
(TR-SEC-013, v0.8 export) in examples/compartmentalized-agents/isolation.py.

Contract under test: each identity sees only its own registered tools (layer
1); each identity is bound by its own data-layer role regardless of what the
tool registry has authorized (layer 2); and layer 2 alone still blocks a
data operation even when layer 1 is deliberately misconfigured -- the
defense-in-depth property the pattern exists for.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

EXAMPLE_DIR = Path(__file__).resolve().parent.parent / "examples" / "compartmentalized-agents"
sys.path.insert(0, str(EXAMPLE_DIR))

from isolation import (  # noqa: E402
    DataAccessError,
    DataStore,
    SelfReportingAgent,
    ToolAuthorizationError,
    ToolRegistry,
)


def test_each_identity_sees_only_its_own_tools() -> None:
    registry = ToolRegistry()
    registry.register("scout", "ingest_url", lambda url: url)
    registry.register("curator", "reorganize_note", lambda note: note)

    assert registry.list_tools("scout") == frozenset({"ingest_url"})
    assert registry.list_tools("curator") == frozenset({"reorganize_note"})


def test_tool_call_by_unregistered_identity_is_rejected() -> None:
    registry = ToolRegistry()
    registry.register("scout", "ingest_url", lambda url: url)

    with pytest.raises(ToolAuthorizationError):
        registry.call("curator", "ingest_url", "http://example.com")


def test_tool_call_for_a_different_tool_the_identity_lacks_is_rejected() -> None:
    """An identity with *some* registered tools must still be rejected for a
    specific tool it wasn't given -- not just an identity with zero tools."""
    registry = ToolRegistry()
    registry.register("curator", "reorganize_note", lambda note: note)

    with pytest.raises(ToolAuthorizationError):
        registry.call("curator", "ingest_url", "http://example.com")


def test_data_layer_enforces_its_own_role_independent_of_tool_registry() -> None:
    store = DataStore()
    store.grant("scout", "inbox", frozenset({"insert"}))
    store.grant("curator", "inbox", frozenset({"select"}))

    store.insert("scout", "inbox", {"url": "http://example.com"})
    assert store.select("curator", "inbox") == [{"url": "http://example.com"}]

    with pytest.raises(DataAccessError):
        store.select("scout", "inbox")  # scout: insert-only, no read-back
    with pytest.raises(DataAccessError):
        store.insert("curator", "inbox", {"url": "http://other.example.com"})  # curator: read-only


def test_data_layer_treats_ungranted_pair_same_as_explicitly_empty_grant() -> None:
    """An (identity, table) pair that was never passed to grant() at all must
    be rejected exactly like one explicitly granted an empty permission set --
    the fail-closed default and an explicit empty grant must not diverge."""
    store = DataStore()
    store.grant("scout", "inbox", frozenset())  # explicit: no permissions

    with pytest.raises(DataAccessError):
        store.select("scout", "inbox")
    with pytest.raises(DataAccessError):
        store.select("curator", "inbox")  # curator: never granted anything on inbox at all


def test_data_layer_still_blocks_when_tool_layer_is_misconfigured() -> None:
    """Simulates the bug class TR-SEC-013 defends against: a tool-registry
    entry wrongly hands an identity a tool that mutates data it should never
    reach. Layer 2 (the data role) must hold regardless of layer 1's bug --
    this is the test that actually proves defense in depth, not just that
    both layers exist independently."""
    store = DataStore()
    store.grant("scout", "inbox", frozenset({"insert", "select"}))
    store.grant("curator", "inbox", frozenset({"select"}))  # curator: read-only on inbox

    registry = ToolRegistry()
    # Simulated authorization-layer bug: curator wrongly registered with
    # scout's insert-capable tool.
    registry.register(
        "curator", "ingest_url", lambda url: store.insert("curator", "inbox", {"url": url})
    )

    # Layer 1 (tool registry) is broken -- curator can invoke the tool.
    assert "ingest_url" in registry.list_tools("curator")

    # Layer 2 (data role) still rejects the resulting write.
    with pytest.raises(DataAccessError):
        registry.call("curator", "ingest_url", "http://example.com")


def test_self_report_can_give_a_false_pass_ground_truth_catches_it() -> None:
    """Reproduces the shape of a real false pass this pattern defends
    against (TR-TEST-007): an isolation check that "passes" because the
    question was answered from a source decoupled from the actual
    enforcement point, not because isolation actually holds."""
    registry = ToolRegistry()
    registry.register("scout", "ingest_url", lambda url: url)
    # Misconfiguration: curator was also (wrongly) granted this tool.
    registry.register("curator", "ingest_url", lambda url: url)

    # curator's self-report was formed before the leak, or answered from a
    # stale/wrong source -- in conversation, it denies having the tool.
    curator_self_report = SelfReportingAgent(identity="curator", believed_tools=frozenset())
    assert curator_self_report.claims_to_have_tool("ingest_url") is False  # looks isolated...

    # ...but the registry -- the actual enforcement point -- shows otherwise.
    # Trusting the self-report alone would have concluded isolation holds;
    # only checking ground truth reveals the real leak.
    assert "ingest_url" in registry.list_tools("curator")
