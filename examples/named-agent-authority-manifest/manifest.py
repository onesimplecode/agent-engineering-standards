"""Fail-closed named-agent authority-manifest reference (TR-AGT-012).

The caller supplies already-parsed configuration. This keeps the pattern
independent of a YAML library and makes the enforcement point explicit: parse
and validate before registering an endpoint.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any


_AGENT_NAME = re.compile(r"^[a-z][a-z0-9_-]{0,62}$")


class AuthorityManifestError(ValueError):
    """A declared named-agent authority manifest is incomplete or invalid."""


def parse_named_agents(config: object) -> dict[str, tuple[str, ...]] | None:
    """Return named allowlists, or ``None`` only when named mode is omitted."""
    if not isinstance(config, Mapping):
        raise AuthorityManifestError("top-level configuration must be a mapping")
    if "api" not in config:
        return None
    api = config["api"]
    if not isinstance(api, Mapping):
        raise AuthorityManifestError("api must be a mapping")
    if "agents" not in api:
        return None
    agents = api["agents"]
    if not isinstance(agents, Mapping) or not agents:
        raise AuthorityManifestError("api.agents must be a non-empty mapping")

    for name in agents:
        if not isinstance(name, str) or not _AGENT_NAME.fullmatch(name):
            raise AuthorityManifestError("agent names must be transport-safe identifiers")

    result: dict[str, tuple[str, ...]] = {}
    for name in sorted(agents):
        agent = agents[name]
        if not isinstance(agent, Mapping):
            raise AuthorityManifestError(f"api.agents.{name} must be a mapping")
        tools = agent.get("tools")
        if not isinstance(tools, list) or not tools:
            raise AuthorityManifestError(f"api.agents.{name}.tools must be a non-empty list")
        if any(not isinstance(tool, str) or not tool.strip() for tool in tools):
            raise AuthorityManifestError(f"api.agents.{name}.tools contains an invalid tool name")
        result[name] = tuple(tools)
    return result


def build_named_registries(
    config: object, registered_tools: Mapping[str, Any]
) -> dict[str, dict[str, Any]]:
    """Validate first, then build an independently scoped registry per identity."""
    manifests = parse_named_agents(config)
    if manifests is None:
        raise AuthorityManifestError("named endpoint builder requires api.agents")

    registries: dict[str, dict[str, Any]] = {}
    for name, tools in manifests.items():
        unknown = sorted(set(tools) - set(registered_tools))
        if unknown:
            raise AuthorityManifestError(f"api.agents.{name} declares unknown tool(s): {unknown}")
        registries[name] = {tool: registered_tools[tool] for tool in tools}
    return registries
