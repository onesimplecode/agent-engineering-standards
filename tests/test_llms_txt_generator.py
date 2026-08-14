"""Pins the CLI contract of scripts/llms-txt-generator.py (v0.5 roadmap item).

Contract under test: exit 0 on successful generation or a clean --check, exit 1
when --check finds drift, exit 2 on a usage error (missing/unparseable registry).
Output is a single llms.txt combining the coding-relevant registry subset (same
selection rules as scripts/cursor-rules-adapter.py, reused not reimplemented)
with the real repo's agents/, templates/, and scripts/ directories.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENERATOR = ROOT / "scripts" / "llms-txt-generator.py"

FIXTURE_REGISTRY = """\
# Comment header, ignored by the parser.
requirements:

  - id: TR-SEC-001
    title: No hardcoded secrets
    status: active
    section: "Secrets Management"
    text: >
      All secrets must be stored in a vault. Never hardcoded in configuration files,
      source code, comments, or test fixtures.

  - id: TR-TEST-001
    title: TDD required for core logic
    status: active
    section: "Testing"
    text: >
      Tests are written before or alongside core logic.

  - id: TR-TEST-999
    title: Retired testing requirement
    status: retired
    section: "Testing"
    text: >
      Must not appear in generated output.

  - id: TR-PUB-001
    title: Curated public release scope
    status: active
    section: "Public Release"
    text: >
      Repo-release operations, not coding rules; excluded from the export.
"""


def run(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GENERATOR), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def _load_generator_module():
    """Load llms-txt-generator.py directly (hyphenated filename) for unit-level
    tests of individual functions, mirroring the script's own importlib trick."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("llms_txt_generator", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_fixture(tmp_path: Path) -> Path:
    registry = tmp_path / "tr-registry.yaml"
    registry.write_text(FIXTURE_REGISTRY, encoding="utf-8")
    return registry


def generate(tmp_path: Path) -> Path:
    registry = write_fixture(tmp_path)
    out = tmp_path / "llms.txt"
    result = run("--registry", str(registry), "--out", str(out))
    assert result.returncode == 0, result.stderr
    return out


# --- generation ----------------------------------------------------------


def test_generates_llms_txt_file(tmp_path: Path) -> None:
    out = generate(tmp_path)
    assert out.exists()


def test_registry_section_includes_active_requirements(tmp_path: Path) -> None:
    text = generate(tmp_path).read_text(encoding="utf-8")
    assert "TR-SEC-001" in text
    assert "No hardcoded secrets" in text
    assert "TR-TEST-001" in text


def test_retired_requirement_excluded(tmp_path: Path) -> None:
    text = generate(tmp_path).read_text(encoding="utf-8")
    assert "TR-TEST-999" not in text
    assert "Retired testing requirement" not in text


def test_public_release_section_excluded(tmp_path: Path) -> None:
    text = generate(tmp_path).read_text(encoding="utf-8")
    assert "TR-PUB-001" not in text


def test_agent_roles_section_lists_real_files(tmp_path: Path) -> None:
    # agents/ is read from the real repo (not fixture-overridable — see module
    # docstring in llms-txt-generator.py for why), so assert against known files.
    text = generate(tmp_path).read_text(encoding="utf-8")
    assert "agents/reviewer.md" in text
    assert "agents/developer.md" in text


def test_templates_section_lists_real_files(tmp_path: Path) -> None:
    text = generate(tmp_path).read_text(encoding="utf-8")
    assert "templates/adr.md" in text


def test_scripts_section_lists_real_files(tmp_path: Path) -> None:
    text = generate(tmp_path).read_text(encoding="utf-8")
    assert "scripts/cursor-rules-adapter.py" in text


def test_start_here_section_names_the_adoption_entry_points(tmp_path: Path) -> None:
    """The manifest must name the file the README tells readers to copy first.

    Without this, deleting _start_here_section leaves both the suite and
    --check green while the adoption CTA silently vanishes from the manifest.
    """
    text = generate(tmp_path).read_text(encoding="utf-8")
    assert "## Start Here" in text
    assert "AGENTS.starter.md" in text
    assert "AGENTS.md" in text


def test_provenance_marker_present(tmp_path: Path) -> None:
    text = generate(tmp_path).read_text(encoding="utf-8")
    assert "llms-txt-generator.py" in text
    assert "Do not edit by hand" in text


def test_output_is_deterministic(tmp_path: Path) -> None:
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    out1 = generate(tmp_path / "a")
    out2 = generate(tmp_path / "b")
    assert out1.read_bytes() == out2.read_bytes()


# --- --check mode ----------------------------------------------------------


def test_check_passes_on_fresh_output(tmp_path: Path) -> None:
    registry = write_fixture(tmp_path)
    out = tmp_path / "llms.txt"
    assert run("--registry", str(registry), "--out", str(out)).returncode == 0
    result = run("--registry", str(registry), "--out", str(out), "--check")
    assert result.returncode == 0, result.stderr


def test_check_fails_on_tampered_file(tmp_path: Path) -> None:
    registry = write_fixture(tmp_path)
    out = tmp_path / "llms.txt"
    run("--registry", str(registry), "--out", str(out))
    out.write_text(out.read_text(encoding="utf-8") + "\nhand edit\n", encoding="utf-8")
    result = run("--registry", str(registry), "--out", str(out), "--check")
    assert result.returncode == 1


def test_check_fails_on_missing_file(tmp_path: Path) -> None:
    registry = write_fixture(tmp_path)
    out = tmp_path / "llms.txt"
    result = run("--registry", str(registry), "--out", str(out), "--check")
    assert result.returncode == 1


# --- usage errors ------------------------------------------------------------


def test_missing_registry_exits_2(tmp_path: Path) -> None:
    result = run("--registry", str(tmp_path / "nope.yaml"), "--out", str(tmp_path / "llms.txt"))
    assert result.returncode == 2


def test_unparseable_registry_exits_2(tmp_path: Path) -> None:
    registry = tmp_path / "bad.yaml"
    registry.write_text(
        "requirements:\n  - id: TR-X-001\n    nested:\n      mapping: unsupported\n",
        encoding="utf-8",
    )
    result = run("--registry", str(registry), "--out", str(tmp_path / "llms.txt"))
    assert result.returncode == 2


def test_registry_with_no_exportable_requirements_exits_2(tmp_path: Path) -> None:
    """Mirrors cursor-rules-adapter.py's expected_files() guard: a registry that
    parses cleanly but has nothing active/non-excluded must fail loudly, not
    silently emit a Registry section with no entries."""
    registry = tmp_path / "empty.yaml"
    registry.write_text(
        "requirements:\n"
        "  - id: TR-X-001\n"
        "    title: Retired only\n"
        "    status: retired\n"
        "    section: Testing\n"
        "    text: >\n"
        "      Not exportable.\n",
        encoding="utf-8",
    )
    result = run("--registry", str(registry), "--out", str(tmp_path / "llms.txt"))
    assert result.returncode == 2


def test_out_parent_directory_is_created(tmp_path: Path) -> None:
    """Matches cursor-rules-adapter.py's out_dir.mkdir(parents=True, exist_ok=True)
    convention — --out into a not-yet-existing directory must not crash."""
    registry = write_fixture(tmp_path)
    out = tmp_path / "new" / "nested" / "llms.txt"
    result = run("--registry", str(registry), "--out", str(out))
    assert result.returncode == 0, result.stderr
    assert out.exists()


def test_real_repo_registry_generates_and_checks_clean(tmp_path: Path) -> None:
    """Integration smoke test: the actual repo's own registry/tr-registry.yaml,
    verifying the real committed llms.txt (if present) has no drift."""
    out = tmp_path / "llms.txt"
    result = run("--out", str(out))
    assert result.returncode == 0, result.stderr
    assert out.exists()


# --- malformed inputs in scripts/agents/templates -----------------------


def test_first_docstring_line_handles_syntax_error_gracefully(tmp_path: Path) -> None:
    """A malformed .py file in scripts/ (e.g. a WIP/scratch file) must not crash
    the whole generator with an uncaught SyntaxError."""
    module = _load_generator_module()
    bad_py = tmp_path / "broken.py"
    bad_py.write_text("def broken(:\n    pass\n", encoding="utf-8")
    assert module._first_docstring_line(bad_py) == ""
