"""Pins the tag-scanning contract of scripts/debt-report.py (TR-GOV-002).

Contract under test: `TECH-DEBT:` and `POC-EXCEPTION:` are the canonical tags;
the pre-rename `LUMIA-DEBT:` is still scanned but reported under `TECH-DEBT`, so
a tree tagged before the rename keeps producing a complete report. The script is
a reporting tool, not a gate — it always exits 0.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "scripts" / "debt-report.py"

_spec = importlib.util.spec_from_file_location("debt_report", REPORT)
_report_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_report_module)


def write_tree(tmp_path: Path, contents: str) -> Path:
    (tmp_path / "sample.py").write_text(contents, encoding="utf-8")
    return tmp_path


def test_canonical_tags_are_collected(tmp_path: Path) -> None:
    root = write_tree(
        tmp_path,
        "# TECH-DEBT: retry budget unbounded [TR-AGT-003]\n"
        "# POC-EXCEPTION: no type checking yet [TR-TEST-002]\n",
    )

    found = _report_module.collect(root)

    assert len(found["TECH-DEBT"]) == 1
    assert len(found["POC-EXCEPTION"]) == 1
    assert "retry budget unbounded" in found["TECH-DEBT"][0][1]


def test_legacy_tag_is_reported_under_the_canonical_name(tmp_path: Path) -> None:
    root = write_tree(tmp_path, "# LUMIA-DEBT: pre-rename tag [TR-GOV-002]\n")

    found = _report_module.collect(root)

    assert "LUMIA-DEBT" not in found
    assert len(found["TECH-DEBT"]) == 1
    assert "pre-rename tag" in found["TECH-DEBT"][0][1]


def test_mixed_canonical_and_legacy_tags_share_one_section(tmp_path: Path) -> None:
    root = write_tree(
        tmp_path,
        "# TECH-DEBT: new style [TR-GOV-002]\n# LUMIA-DEBT: old style [TR-GOV-002]\n",
    )

    found = _report_module.collect(root)
    rendered = _report_module.render(found)

    assert len(found["TECH-DEBT"]) == 2
    assert "## TECH-DEBT (2)" in rendered
    assert "LUMIA-DEBT" not in rendered


def test_empty_tree_reports_canonical_tag_names(tmp_path: Path) -> None:
    rendered = _report_module.render(_report_module.collect(write_tree(tmp_path, "x = 1\n")))

    assert "No `TECH-DEBT:` or `POC-EXCEPTION:` tags found." in rendered


def test_convention_defining_files_are_excluded_from_scanning() -> None:
    """Files that document the tag convention contain the tag strings as
    examples, not as real deferred work. This test file is one of them — without
    the exclusion, its own fixtures show up as findings in the repo's report."""
    root = Path(__file__).resolve().parent.parent

    found = _report_module.collect(root)
    locations = [loc for entries in found.values() for loc, _ in entries]

    assert "tests/test_debt_report.py" in _report_module.EXCLUDE_FILES
    assert not [loc for loc in locations if loc.startswith("tests/test_debt_report.py")]
    assert not [loc for loc in locations if loc.startswith("scripts/debt-report.py")]


def test_cli_always_exits_zero(tmp_path: Path) -> None:
    root = write_tree(tmp_path, "# TECH-DEBT: something deferred [TR-GOV-002]\n")

    result = subprocess.run(
        [sys.executable, str(REPORT), "--path", str(root)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )

    assert result.returncode == 0
    assert "TECH-DEBT" in result.stdout
