"""Reference implementation: two-layer isolation for multi-agent tool and
data access (TR-SEC-013).

Two agents share one backing service (a tool surface and the data behind
it). Isolation is enforced at two independent layers:

1. ToolRegistry -- what's *offered* to a given agent's own reasoning. Each
   agent gets its own credential (``identity``) and its own registered tool
   set. This is an authorization-layer boundary: it controls what an agent
   can even attempt, but a bug here (a stray wildcard registration, a
   misrouted credential map) can still hand an agent a tool it should never
   have gotten.
2. DataStore -- what's *reachable* even if layer 1 has a bug. A per-identity
   role on the underlying data, enforced independently of whatever the tool
   registry believes it has authorized.

Neither layer is a substitute for the other -- see
test_data_layer_still_blocks_when_tool_layer_is_misconfigured in the test
file for a simulated layer-1 bug that layer 2 alone catches.

A third piece, SelfReportingAgent, illustrates TR-TEST-007: verifying a
security property (like the isolation above) by asking an agent about its
own state, in conversation, is not evidence -- only querying the actual
enforcement point (ToolRegistry, here) is. See
test_self_report_can_give_a_false_pass_ground_truth_catches_it in the test
file.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class ToolAuthorizationError(PermissionError):
    """Raised when an identity calls a tool it was never registered for."""


class DataAccessError(PermissionError):
    """Raised when an identity performs a data operation its role doesn't grant."""


@dataclass
class ToolRegistry:
    """Layer 1: per-identity tool offering, enforced by the server, not the agent."""

    _tools: dict[str, dict[str, object]] = field(default_factory=dict)

    def register(self, identity: str, tool_name: str, fn) -> None:
        self._tools.setdefault(identity, {})[tool_name] = fn

    def list_tools(self, identity: str) -> frozenset[str]:
        """What this identity can even see -- used to assert isolation directly,
        not inferred from asking the agent what it thinks it can do."""
        return frozenset(self._tools.get(identity, {}).keys())

    def call(self, identity: str, tool_name: str, *args, **kwargs):
        tools = self._tools.get(identity, {})
        if tool_name not in tools:
            raise ToolAuthorizationError(f"{identity!r} has no tool {tool_name!r}")
        return tools[tool_name](*args, **kwargs)


Permission = str  # "insert" | "select"


@dataclass
class DataStore:
    """Layer 2: per-identity data role, independent of the tool registry above."""

    _rows: dict[str, list[dict]] = field(default_factory=dict)
    _roles: dict[tuple[str, str], frozenset[Permission]] = field(default_factory=dict)

    def grant(self, identity: str, table: str, permissions: frozenset[Permission]) -> None:
        self._roles[(identity, table)] = permissions

    def insert(self, identity: str, table: str, row: dict) -> None:
        if "insert" not in self._roles.get((identity, table), frozenset()):
            raise DataAccessError(f"{identity!r} has no insert permission on {table!r}")
        self._rows.setdefault(table, []).append(row)

    def select(self, identity: str, table: str) -> list[dict]:
        if "select" not in self._roles.get((identity, table), frozenset()):
            raise DataAccessError(f"{identity!r} has no select permission on {table!r}")
        return list(self._rows.get(table, []))


@dataclass
class SelfReportingAgent:
    """Simulates asking an agent, in conversation, whether it has some
    capability (TR-TEST-007).

    ``believed_tools`` is a snapshot the agent formed independently of the
    registry -- at onboarding, from a stale cache, or from a question
    answered by the wrong backend entirely -- deliberately decoupled from
    ToolRegistry so it can drift out of sync with it, the same way an
    agent's chat answer to "do you have tool X" is decoupled from whatever
    actually enforces access. ``claims_to_have_tool`` is what the agent
    *says*, not verification evidence.
    """

    identity: str
    believed_tools: frozenset[str]

    def claims_to_have_tool(self, tool_name: str) -> bool:
        return tool_name in self.believed_tools
