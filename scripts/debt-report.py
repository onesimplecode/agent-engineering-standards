#!/usr/bin/env python3
"""
TR-GOV-002 — Deferred-work tagging convention report.

Scans the repo for inline tags:

    TECH-DEBT: <description> (<TR-ID or rationale>)
    POC-EXCEPTION: <TR-ID> <description>

`LUMIA-DEBT:` is accepted as a legacy alias for `TECH-DEBT:` and reported under
the canonical name, so trees tagged before the rename keep scanning clean.

and compiles them into a markdown report grouped by tag type and referenced
TR-ID. Use this to populate the "Evidence/Notes" column of a per-app
docs/maturity-checklist.md (TR-GOV-004) and to reconcile open items before a
tier graduation.

Usage:
    python3 scripts/debt-report.py [--path PATH]

Always exits 0 — this is a reporting tool, not a gate.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIR_NAMES = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".pytest_cache", ".ruff_cache", "data", "logs", ".pages_repo",
    "site_template", "egg-info", "dist", "build",
}

# Files that define or describe the tagging convention itself (and therefore
# contain the tag strings as examples, not as real deferred-work markers).
EXCLUDE_FILES = {
    "scripts/debt-report.py",
    "tests/test_debt_report.py",
    "docs/tr-registry.yaml",
    "registry/tr-registry.yaml",
}

# Binary-ish extensions to skip outright.
SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".db", ".sqlite", ".sqlite3",
    ".pyc", ".lock", ".woff", ".woff2", ".ico", ".zip", ".gz",
}

CANONICAL_TAGS = ("TECH-DEBT", "POC-EXCEPTION")
# Pre-rename tag; still scanned, reported under its canonical name.
LEGACY_TAG_ALIASES = {"LUMIA-DEBT": "TECH-DEBT"}

TAG_PATTERN = re.compile(
    r"\b(" + "|".join((*CANONICAL_TAGS, *LEGACY_TAG_ALIASES)) + r"):\s*(.*)$"
)
TR_ID_PATTERN = re.compile(r"TR-[A-Z]+-\d+")


def iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        if any(part in EXCLUDE_DIR_NAMES for part in path.parts):
            continue
        if path.relative_to(root).as_posix() in EXCLUDE_FILES:
            continue
        yield path


def collect(root: Path) -> dict[str, list[tuple[str, str]]]:
    """Return {tag_type: [(location, rest_of_line), ...]}."""
    found: dict[str, list[tuple[str, str]]] = {tag: [] for tag in CANONICAL_TAGS}
    for path in iter_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            m = TAG_PATTERN.search(line)
            if not m:
                continue
            tag, rest = m.group(1), m.group(2).strip()
            tag = LEGACY_TAG_ALIASES.get(tag, tag)
            rel = path.relative_to(root)
            found[tag].append((f"{rel}:{lineno}", rest))
    return found


def render(found: dict[str, list[tuple[str, str]]]) -> str:
    total = sum(len(v) for v in found.values())
    lines = ["# Deferred Work Report (TR-GOV-002)", ""]
    if total == 0:
        lines.append("No `TECH-DEBT:` or `POC-EXCEPTION:` tags found.")
        return "\n".join(lines)

    for tag, entries in found.items():
        lines.append(f"## {tag} ({len(entries)})")
        lines.append("")
        if not entries:
            lines.append("_None._")
            lines.append("")
            continue

        # Group by referenced TR-ID, "untagged" if none found.
        by_tr: dict[str, list[tuple[str, str]]] = {}
        for location, rest in entries:
            tr_ids = TR_ID_PATTERN.findall(rest) or ["(no TR-ID referenced)"]
            for tr_id in tr_ids:
                by_tr.setdefault(tr_id, []).append((location, rest))

        for tr_id in sorted(by_tr):
            lines.append(f"### {tr_id}")
            for location, rest in by_tr[tr_id]:
                lines.append(f"- `{location}`: {rest}")
            lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", default=str(REPO_ROOT), help="Root path to scan (default: repo root)")
    args = parser.parse_args()

    found = collect(Path(args.path).resolve())
    print(render(found))
    return 0


if __name__ == "__main__":
    sys.exit(main())
