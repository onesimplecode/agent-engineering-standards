"""Tests the fail-closed provenance trust mapping reference implementation
(TR-SEC-011, v0.7 export) in examples/provenance-trust-tags/trust.py.

Contract under test: every ContentType member is explicitly classified (the
drift guard); an unrecognized/future type and a missing source_type both
resolve to a quarantined trust level, never to "trusted" or "derived".
"""

from __future__ import annotations

import sys
from pathlib import Path

EXAMPLE_DIR = Path(__file__).resolve().parent.parent / "examples" / "provenance-trust-tags"
sys.path.insert(0, str(EXAMPLE_DIR))

from trust import (  # noqa: E402
    QUARANTINED_LEVELS,
    SOURCE_TRUST_MAP,
    ContentType,
    UNVERIFIED,
    is_quarantined,
    trust_level_for,
)


def test_drift_guard_every_content_type_is_classified() -> None:
    unclassified = [ct for ct in ContentType if ct not in SOURCE_TRUST_MAP]
    assert unclassified == [], (
        f"ContentType member(s) missing from SOURCE_TRUST_MAP: {unclassified} -- "
        "classify their trust level explicitly, don't rely on the fail-closed default"
    )


def test_user_authored_and_assistant_derived_are_the_only_non_untrusted_tiers() -> None:
    trusted_or_derived = {
        ct for ct, level in SOURCE_TRUST_MAP.items() if level in ("trusted", "derived")
    }
    assert trusted_or_derived == {ContentType.USER_AUTHORED, ContentType.ASSISTANT_DERIVED}


def test_known_untrusted_types_resolve_correctly() -> None:
    for ct in (ContentType.WEB_ARTICLE, ContentType.THIRD_PARTY_REPO, ContentType.UNKNOWN):
        assert trust_level_for(ct) == "untrusted"


def test_missing_source_type_resolves_to_unverified_not_trusted() -> None:
    assert trust_level_for(None) == UNVERIFIED


def test_unrecognized_future_type_fails_closed_to_untrusted() -> None:
    # Simulate a ContentType member added later without being added to
    # SOURCE_TRUST_MAP -- the .get(..., default) fallback must never resolve
    # to "trusted" or "derived".
    class _FutureType:
        pass

    result = trust_level_for(_FutureType())  # type: ignore[arg-type]
    assert result == "untrusted"


def test_quarantine_covers_untrusted_and_unverified_never_trusted_or_derived() -> None:
    assert QUARANTINED_LEVELS == frozenset({"untrusted", UNVERIFIED})
    assert is_quarantined("untrusted") is True
    assert is_quarantined(UNVERIFIED) is True
    assert is_quarantined("trusted") is False
    assert is_quarantined("derived") is False
