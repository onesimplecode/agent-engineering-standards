import sys
from pathlib import Path

import pytest

EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples" / "credential-isolated-broker"
sys.path.insert(0, str(EXAMPLE_DIR))

from broker import Broker, BrokerError  # noqa: E402


def test_scope_and_revision_are_bound_to_single_use_lease() -> None:
    broker = Broker("repo/pr-10")
    lease = broker.issue_lease("repo/pr-10", "event-1", "sha-a")
    assert broker.consume_mutation(
        lease, resource="repo/pr-10", event_id="event-1", revision="sha-a", current_revision="sha-a"
    ) == "mutation-authorized"
    with pytest.raises(BrokerError, match="consumed"):
        broker.consume_mutation(
            lease, resource="repo/pr-10", event_id="event-1", revision="sha-a", current_revision="sha-a"
        )


def test_stale_revision_and_wrong_scope_fail_closed() -> None:
    broker = Broker("repo/pr-10")
    with pytest.raises(BrokerError):
        broker.issue_lease("repo/pr-11", "event-1", "sha-a")
    lease = broker.issue_lease("repo/pr-10", "event-1", "sha-a")
    with pytest.raises(BrokerError, match="stale"):
        broker.consume_mutation(
            lease, resource="repo/pr-10", event_id="event-1", revision="sha-a", current_revision="sha-b"
        )
