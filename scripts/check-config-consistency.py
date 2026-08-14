#!/usr/bin/env python3
"""
TR-GOV-001 — Config/model-string consistency check.

Scans each app's CLAUDE.md, config files, and ADRs for:
  1. RETIRED strings that must never appear (known-invalid IDs, e.g. an
     OpenRouter model string that doesn't exist).
  2. DRIFT — more than one distinct value for the same "constant family"
     (e.g. a Kimi model version, a local Gemma size) within a single app.

This operationalizes the "single source of truth for configurable strings" rule
described in AGENTS.md. It does not require any third-party dependency.

Usage:
    python3 scripts/check-config-consistency.py [--root PATH] [--app APPNAME ...]

Exit code 0 if clean, 1 if any retired string or drift is found, 2 on a
usage error (--root doesn't exist, an --app name that doesn't resolve to a
scanned directory, or zero apps discovered under --root).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Directories that contain noise (deps, caches, generated output) and must
# never be scanned.
EXCLUDE_DIR_NAMES = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".pytest_cache", ".ruff_cache", "data", "logs", ".pages_repo",
    "site_template", "egg-info",
}

# Relative globs (within an app directory) that are in scope.
SCAN_GLOBS = [
    "CLAUDE.md",
    "config/*.yaml",
    "config/*.yaml.example",
    "config/*.yml",
    "config/*.json",
    "config/*.example",
    ".env.example",
    "docs/decisions/*.md",
]

# Strings that must never appear anywhere in the repo, with a hint for the fix.
RETIRED_STRINGS: dict[str, str] = {
    "google/gemini-flash-2.5": "invalid OpenRouter model ID; replace with the configured source-of-truth model ID",
}

# "Constant families": each app must use exactly one value per family across
# all scanned files. Pattern groups are matched case-insensitively; the
# matched text is lower-cased before deduplication.
FAMILY_PATTERNS: dict[str, re.Pattern[str]] = {
    "kimi-model": re.compile(r"(?:moonshotai/)?kimi-k2(?:\.\d+)?", re.IGNORECASE),
    "gemini-flash-model": re.compile(r"(?:google/)?gemini-flash[-.\w]*", re.IGNORECASE),
    "local-gemma-model": re.compile(r"gemma\d*[:\-]\d+b", re.IGNORECASE),
}


def discover_apps(root: Path) -> list[Path]:
    """Top-level directories containing a CLAUDE.md are treated as apps."""
    apps = []
    for child in sorted(root.iterdir()):
        if child.is_dir() and child.name not in EXCLUDE_DIR_NAMES and not child.name.startswith("."):
            if (child / "CLAUDE.md").exists():
                apps.append(child)
    return apps


def scan_files(app_dir: Path) -> list[Path]:
    # dict, not list/set: some SCAN_GLOBS overlap (e.g. "config/*.yaml.example" and
    # "config/*.example" both match "search_config.yaml.example"); dedupe by path
    # while preserving order so a file isn't scanned — and its lines double-counted
    # in DRIFT locations — once per matching glob.
    seen: dict[Path, None] = {}
    for pattern in SCAN_GLOBS:
        for f in sorted(app_dir.glob(pattern)):
            if f.is_file():
                seen.setdefault(f, None)
    return list(seen)


def check_app(app_dir: Path, root: Path) -> list[str]:
    """Return a list of human-readable issue lines for one app."""
    issues: list[str] = []
    # family -> normalized value -> list of "file:line"
    family_hits: dict[str, dict[str, list[str]]] = {f: {} for f in FAMILY_PATTERNS}

    for path in scan_files(app_dir):
        rel = path.relative_to(root)
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue

        for lineno, line in enumerate(lines, start=1):
            for retired, hint in RETIRED_STRINGS.items():
                if retired.lower() in line.lower():
                    issues.append(
                        f"  RETIRED  {rel}:{lineno}: found {retired!r} — {hint}"
                    )

            for family, pattern in FAMILY_PATTERNS.items():
                for match in pattern.finditer(line):
                    value = match.group(0).lower()
                    family_hits[family].setdefault(value, []).append(f"{rel}:{lineno}")

    for family, values in family_hits.items():
        if len(values) > 1:
            issues.append(f"  DRIFT    {family}: {len(values)} distinct values found")
            for value, locations in values.items():
                issues.append(f"             {value!r} <- {', '.join(locations)}")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", default=str(REPO_ROOT),
        help="Repo root to scan for app directories (default: this script's own repo root).",
    )
    parser.add_argument(
        "--app", action="append", dest="apps",
        help="Limit to one or more app directory names (repeatable). Default: all apps.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"--root does not exist or is not a directory: {root}", file=sys.stderr)
        return 2
    discovered = discover_apps(root)

    if args.apps:
        known_names = {a.name for a in discovered}
        unknown = [name for name in args.apps if name not in known_names]
        if unknown:
            print(f"Unknown app(s): {', '.join(unknown)}. Known: {', '.join(sorted(known_names))}", file=sys.stderr)
            return 2
        apps = [a for a in discovered if a.name in args.apps]
    else:
        apps = discovered

    if not apps:
        print(f"No apps discovered under {root} (looked for a CLAUDE.md in each top-level directory).", file=sys.stderr)
        return 2

    any_issue = False
    for app_dir in apps:
        issues = check_app(app_dir, root)
        if issues:
            any_issue = True
            print(f"{app_dir.name}:")
            for issue in issues:
                print(issue)

    if not any_issue:
        print(f"OK — checked {len(apps)} app(s), no retired strings or config drift found.")
        return 0

    print("\nSee TR-GOV-001 (registry/tr-registry.yaml) for the convention this enforces.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
