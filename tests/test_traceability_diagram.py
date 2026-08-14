"""Gates the README's centerpiece diagram against the files it claims exist.

`docs/assets/traceability.svg` is hand-authored and rendered at the top of
README.md under the repo's differentiator claim. Its caption asserts two things:
that every stage is a real file, and that every stage names TR-GOV-001. Both are
silently falsifiable by an ordinary rename, and two review passes caught the
diagram overclaiming in two different ways before this test existed.

The SVG is not generated, so these tests pin its claims rather than its shape.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SVG = ROOT / "docs" / "assets" / "traceability.svg"
README = ROOT / "README.md"

REQUIREMENT_ID = "TR-GOV-001"

# The five stages, in order. Each is (path, why it belongs in the chain).
STAGES = [
    ("registry/tr-registry.yaml", "requirement is defined"),
    ("AGENTS.md", "convention the agent reads"),
    ("examples/worked-example/docs/maturity-checklist.md", "status row"),
    ("scripts/check-config-consistency.py", "deterministic check"),
    (".github/workflows/config-drift-demo.yml", "CI gate"),
]


def svg_text() -> str:
    return SVG.read_text(encoding="utf-8")


def test_svg_is_valid_xml() -> None:
    ET.parse(SVG)


def test_every_stage_file_exists() -> None:
    missing = [path for path, _ in STAGES if not (ROOT / path).exists()]
    assert not missing, f"diagram names paths that do not exist: {missing}"


def test_every_stage_file_names_the_requirement() -> None:
    """The caption claims every stage names TR-GOV-001 — verify each one does."""
    silent = [
        path
        for path, _ in STAGES
        if REQUIREMENT_ID not in (ROOT / path).read_text(encoding="utf-8", errors="ignore")
    ]
    assert not silent, f"stages that do not mention {REQUIREMENT_ID}: {silent}"


def test_svg_labels_match_the_stage_list() -> None:
    """Guards the other direction: a path drawn in the SVG but absent from
    STAGES would escape the existence check above."""
    text = svg_text()
    drawn = set(re.findall(r"[\w./-]+\.(?:yaml|yml|md|py)", text))
    known = {Path(path).name for path, _ in STAGES} | {
        "traceability.svg", "llms-txt-generator.py",
    }
    unknown = {d for d in drawn if Path(d).name not in known}
    assert not unknown, f"SVG draws unrecognized paths, add them to STAGES: {unknown}"


def test_readme_renders_the_diagram() -> None:
    assert "docs/assets/traceability.svg" in README.read_text(encoding="utf-8")


def test_caption_requirement_matches_the_stage_list() -> None:
    assert REQUIREMENT_ID in svg_text()
