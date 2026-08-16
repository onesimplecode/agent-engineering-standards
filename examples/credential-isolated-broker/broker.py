"""Small reference broker: scope-bound, immutable, single-use mutation leases."""

from dataclasses import dataclass


class BrokerError(ValueError):
    """Raised for invalid, stale, out-of-scope, or replayed operations."""


@dataclass(frozen=True)
class Lease:
    resource: str
    event_id: str
    revision: str


class Broker:
    def __init__(self, allowed_resource: str) -> None:
        self.allowed_resource = allowed_resource
        self._leases: dict[str, Lease] = {}

    def issue_lease(self, resource: str, event_id: str, revision: str) -> str:
        self._validate(resource, event_id, revision)
        token = f"lease-{len(self._leases) + 1}"
        self._leases[token] = Lease(resource, event_id, revision)
        return token

    def consume_mutation(self, token: str, *, resource: str, event_id: str,
                         revision: str, current_revision: str) -> str:
        lease = self._leases.pop(token, None)
        if lease is None:
            raise BrokerError("invalid or consumed lease")
        self._validate(resource, event_id, revision)
        if lease != Lease(resource, event_id, revision) or current_revision != revision:
            raise BrokerError("stale or mismatched event identity")
        return "mutation-authorized"

    def _validate(self, resource: str, event_id: str, revision: str) -> None:
        if resource != self.allowed_resource:
            raise BrokerError("resource out of scope")
        if not event_id or not revision:
            raise BrokerError("immutable event identity is required")
