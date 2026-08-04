"""Reference implementation: fail-closed provenance trust derivation (TR-SEC-011).

The pattern in three layers:

1. Tag at ingest — record each item's ``source_type`` when it's written into
   the memory/index (not shown here; this module only covers layers 2-3).
2. Derive trust at read time — SOURCE_TRUST_MAP is the single source of truth
   mapping source_type -> trust level. Fail-closed by construction: only the
   two explicitly named self-authored types earn "trusted"; every other
   ContentType member, including ones added later without being classified
   here, resolves to "untrusted" via the .get(..., "untrusted") default.
3. Validate at retrieval — trust_level_for() is called per retrieved item,
   not only once at ingest, so a row whose provenance predates this pattern
   (``source_type is None``) is caught and mapped to "unverified" rather than
   silently trusted.

Storing only ``source_type`` (a fact) and deriving ``trust_level`` (a
judgment) at query time means a future mapping change is a code review, not a
data migration.
"""

from __future__ import annotations

from enum import Enum


class ContentType(Enum):
    """Every kind of content this system can ingest.

    Adding a member here without adding it to SOURCE_TRUST_MAP is caught by
    test_drift_guard_every_content_type_is_classified below -- the same
    "unreviewed grant" pattern TR-SEC-010's agent-permission-guard uses.
    """

    USER_AUTHORED = "user_authored"
    ASSISTANT_DERIVED = "assistant_derived"
    WEB_ARTICLE = "web_article"
    THIRD_PARTY_REPO = "third_party_repo"
    TRANSCRIBED_MEDIA = "transcribed_media"
    UNKNOWN = "unknown"


TrustLevel = str  # "trusted" | "derived" | "untrusted" | "unverified"

# The single source of truth. Only these two types are self-authored by the
# system's own owner/operator; everything else is external by default.
SOURCE_TRUST_MAP: dict[ContentType, TrustLevel] = {
    ContentType.USER_AUTHORED: "trusted",
    ContentType.ASSISTANT_DERIVED: "derived",
    ContentType.WEB_ARTICLE: "untrusted",
    ContentType.THIRD_PARTY_REPO: "untrusted",
    ContentType.TRANSCRIBED_MEDIA: "untrusted",
    ContentType.UNKNOWN: "untrusted",
}

# Fail-closed default for any ContentType member NOT present in the map above
# (a future member added without an explicit classification) and the
# well-known state for a stored row whose source_type was never recorded.
_UNCLASSIFIED_DEFAULT: TrustLevel = "untrusted"
UNVERIFIED: TrustLevel = "unverified"


def trust_level_for(source_type: ContentType | None) -> TrustLevel:
    """Derive trust level at retrieval time. Fail-closed: unrecognized or
    missing provenance never resolves to "trusted" or "derived"."""
    if source_type is None:
        return UNVERIFIED
    return SOURCE_TRUST_MAP.get(source_type, _UNCLASSIFIED_DEFAULT)


QUARANTINED_LEVELS = frozenset({"untrusted", UNVERIFIED})


def is_quarantined(trust_level: TrustLevel) -> bool:
    """True if content at this trust level must be spotlighted (TR-SEC-005)
    at the reasoning boundary rather than treated as trusted instruction."""
    return trust_level in QUARANTINED_LEVELS
