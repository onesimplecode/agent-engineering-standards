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


def test_failed_validation_does_not_burn_the_lease() -> None:
    """A stale/mismatched attempt must not consume a lease a legitimate retry still needs.

    Regression: consume_mutation used to pop the lease before validating, so one bad
    or racy attempt (e.g. a stale current_revision) permanently destroyed an
    otherwise-valid lease, turning a validation failure into a denial-of-service on
    the legitimate caller's own retry.
    """
    broker = Broker("repo/pr-10")
    lease = broker.issue_lease("repo/pr-10", "event-1", "sha-a")
    with pytest.raises(BrokerError, match="stale"):
        broker.consume_mutation(
            lease, resource="repo/pr-10", event_id="event-1", revision="sha-a", current_revision="sha-b"
        )
    assert broker.consume_mutation(
        lease, resource="repo/pr-10", event_id="event-1", revision="sha-a", current_revision="sha-a"
    ) == "mutation-authorized"
