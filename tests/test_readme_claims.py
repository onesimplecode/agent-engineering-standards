"""Gates the factual claims README.md makes about this repo.

The README's first screen asserts asset counts and a test count as evidence that
this is a working toolkit rather than a prose collection. Those numbers are
hand-written in two places (the shields.io test badge and the asset-count line),
so nothing stops them drifting the next time a script or example is added — the
failure is silent and lands on the most-read line of the announcement.

These tests make the claims self-checking: add an example, and the README must be
updated in the same change or CI fails.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"

# "**7 scripts · 13 worked examples · 9 templates · 37 requirement IDs · 118 tests.**"
COUNT_LINE = re.compile(
    r"\*\*(\d+) scripts · (\d+) worked examples · (\d+) templates · "
    r"(\d+) requirement IDs · (\d+) tests\.\*\*"
)
# "![Tests](https://img.shields.io/badge/tests-118%20passing-brightgreen)"
TEST_BADGE = re.compile(r"img\.shields\.io/badge/tests-(\d+)%20passing")


def readme_counts() -> tuple[int, int, int, int, int]:
    match = COUNT_LINE.search(README.read_text(encoding="utf-8"))
    assert match, "README asset-count line is missing or reworded; update this test too"
    return tuple(int(g) for g in match.groups())  # type: ignore[return-value]


def collected_test_count() -> int:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "--collect-only", "-q"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    match = re.search(r"(\d+) tests? collected", result.stdout)
    assert match, f"could not parse pytest collection output:\n{result.stdout}"
    return int(match.group(1))


def test_script_count_matches_readme() -> None:
    scripts, _, _, _, _ = readme_counts()
    assert scripts == len(list((ROOT / "scripts").glob("*.py")))


def test_example_count_matches_readme() -> None:
    _, examples, _, _, _ = readme_counts()
    assert examples == len([p for p in (ROOT / "examples").iterdir() if p.is_dir()])


def test_template_count_matches_readme() -> None:
    _, _, templates, _, _ = readme_counts()
    assert templates == len(list((ROOT / "templates").glob("*.md")))


def test_requirement_id_count_matches_readme() -> None:
    _, _, _, requirement_ids, _ = readme_counts()
    registry = (ROOT / "registry" / "tr-registry.yaml").read_text(encoding="utf-8")
    assert requirement_ids == len(re.findall(r"^  - id:", registry, re.MULTILINE))


def test_test_count_matches_readme_line_and_badge() -> None:
    """The count appears twice — the asset line and the badge — and both drift."""
    _, _, _, _, claimed = readme_counts()
    badge = TEST_BADGE.search(README.read_text(encoding="utf-8"))
    assert badge, "README test badge is missing or reworded; update this test too"

    actual = collected_test_count()
    assert claimed == actual
    assert int(badge.group(1)) == actual


def fenced_blocks(path: Path) -> list[str]:
    return re.findall(r"^```(?:\w+)?\n(.*?)^```", path.read_text(encoding="utf-8"),
                      re.MULTILINE | re.DOTALL)


def test_readme_proof_block_matches_real_command_output() -> None:
    """The README's central credibility claim is that this output is real.

    A visitor's first action is running this command and diffing it against the
    page. Any drift — a reworded message, a changed path — turns the repo's
    honest-evidence pitch into its own counterexample.
    """
    result = subprocess.run(
        [sys.executable, "scripts/agent-permission-guard.py", "--settings",
         "examples/agent-permission-guard/settings.example.json"],
        capture_output=True, text=True, cwd=ROOT,
    )
    actual = (result.stdout + result.stderr).strip()

    assert result.returncode == 1, "README claims exit code 1"
    assert any(block.strip() == actual for block in fenced_blocks(README)), (
        f"no fenced block in README.md matches real output:\n---actual---\n{actual}"
    )


def test_worked_example_output_block_matches_real_command_output() -> None:
    """Same claim, made by the example the README links as the traceability proof."""
    example = ROOT / "examples" / "worked-example"
    result = subprocess.run(
        [sys.executable, "scripts/check-config-consistency.py", "--root", str(example)],
        capture_output=True, text=True, cwd=ROOT,
    )
    actual = (result.stdout + result.stderr).strip()

    assert result.returncode == 1, "the planted drift must still be detected"
    assert any(block.strip() == actual for block in fenced_blocks(example / "README.md")), (
        f"no fenced block in the worked example matches real output:\n---actual---\n{actual}"
    )


def test_every_gallery_row_points_at_a_real_example() -> None:
    """The gallery is the README's proof that each failure has a worked example."""
    text = README.read_text(encoding="utf-8")
    linked = set(re.findall(r"\[`(examples/[^`]+)/`\]", text))
    on_disk = {f"examples/{p.name}" for p in (ROOT / "examples").iterdir() if p.is_dir()}

    assert not linked - on_disk, f"README links to missing examples: {linked - on_disk}"
    assert not on_disk - linked, f"examples missing from the README gallery: {on_disk - linked}"
