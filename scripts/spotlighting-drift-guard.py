#!/usr/bin/env python3
"""
TR-SEC-005 -- Spotlighting drift guard (single-sourced untrusted-content markers).

Spotlighting delimits untrusted retrieved/external content so an LLM can treat
it as data, not instructions -- Microsoft's measurements put this at cutting
indirect prompt-injection success from >50% to <2%. The security-notice and
delimiter strings that implement it are security-critical text: every LLM
boundary that consumes untrusted content must use the byte-identical wording,
or the boundaries silently drift apart (exactly what happened privately before
this pattern existed -- two call sites' notice text drifted by a few words
while nobody noticed).

This script enforces "single-sourced, never re-inlined": it reads the literal
string constants defined in one designated --constants-file, then fails if any
of those same literal values appear hardcoded anywhere else under --scan-root.
A second LLM boundary that needs the same notice/delimiter must import the
constant, not paste its value.

Honest limits: this is a friction control, not a barrier (see
templates/threat-model.md's Impossible vs. Tedious section) -- it catches
accidental re-inlining a human is expected to notice in review. It does not
stop a determined author from editing both the constants file and this
script's exclusions in the same commit; branch protection and human review of
that diff are the real backstop. It also doesn't distinguish a re-inlined
security string from a legitimate quote of it (e.g. documentation explaining
the exact wording), and a file this script can't decode as UTF-8 is silently
skipped rather than flagged -- both are accepted trade-offs for a script
meant to run unattended in CI against a large source tree.

Usage:
    python3 scripts/spotlighting-drift-guard.py \\
        --constants-file path/to/module_with_constants.py \\
        --scan-root path/to/src

Exit code 0 if no constant value is re-inlined outside the constants file, 1
if any re-inlined copy is found, 2 on a usage error (missing/unreadable file,
no string constants found).
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

# A constant worth drift-guarding is a module-level UPPER_SNAKE assignment to
# a non-trivial string literal -- short values (e.g. "" or a single
# character) are excluded to avoid flooding the scan with false positives.
_MIN_LITERAL_LENGTH = 12

# Directories never worth walking when scanning a downstream repo's source
# tree -- matches the convention in scripts/public-export-check.py and
# scripts/check-config-consistency.py, extended with the dependency/venv
# directories a real --scan-root is likely to contain.
_SKIP_PATH_PARTS = {
    ".git", "__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache",
    ".venv", "venv", "node_modules",
}


def load_constants(path: Path) -> dict[str, str]:
    """Parse module-level UPPER_SNAKE string-constant assignments via the AST
    (not a line-oriented regex) so multi-line and implicitly-concatenated
    string literals -- e.g. a security notice split across several quoted
    lines -- are read as their full, true value rather than truncated at the
    first line break.
    """
    if not path.is_file():
        print(f"ERROR: constants file not found: {path}", file=sys.stderr)
        sys.exit(2)
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"ERROR: {path} could not be parsed as Python: {e}", file=sys.stderr)
        sys.exit(2)

    constants: dict[str, str] = {}
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value_node = node.targets[0], node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            target, value_node = node.target, node.value
        else:
            continue
        if not (isinstance(target, ast.Name) and target.id.isupper()):
            continue
        try:
            value = ast.literal_eval(value_node)
        except (ValueError, TypeError):
            continue
        if isinstance(value, str) and len(value) >= _MIN_LITERAL_LENGTH:
            constants[target.id] = value

    if not constants:
        print(
            f"ERROR: no UPPER_SNAKE string constants (>= {_MIN_LITERAL_LENGTH} chars) "
            f"found in {path}",
            file=sys.stderr,
        )
        sys.exit(2)
    return constants


def _python_string_literals(text: str) -> set[str]:
    """All string-literal constant values appearing anywhere in a Python
    source file, with implicitly-concatenated / parenthesized multi-line
    literals already folded into their single true value by ast.parse.
    Returns an empty set for non-Python or unparseable text -- this is a
    supplementary check, not the only one (see find_reinlined_copies)."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        and len(node.value) >= _MIN_LITERAL_LENGTH
    }


def find_reinlined_copies(
    constants: dict[str, str], scan_root: Path, constants_file: Path
) -> list[str]:
    violations: list[str] = []
    skipped_unreadable: list[Path] = []
    constants_file_resolved = constants_file.resolve()
    for candidate in sorted(scan_root.rglob("*")):
        if not candidate.is_file() or set(candidate.parts) & _SKIP_PATH_PARTS:
            continue
        if candidate.resolve() == constants_file_resolved:
            continue
        try:
            text = candidate.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            skipped_unreadable.append(candidate)
            continue
        # Raw substring search catches a re-inlined copy in any file type
        # (including a single-line Python string, or a non-Python doc/config
        # file). Python source additionally gets an AST-literal check, so a
        # copy split across implicitly-concatenated lines -- invisible to a
        # raw substring search, since the source text never contains the
        # joined value contiguously -- is still caught.
        python_literals = _python_string_literals(text) if candidate.suffix == ".py" else set()
        for name, value in constants.items():
            if value in text or value in python_literals:
                violations.append(
                    f"DRIFT {candidate}: re-inlines the literal value of "
                    f"{name} (defined in {constants_file}) instead of importing it"
                )
    if skipped_unreadable:
        print(
            f"NOTE: skipped {len(skipped_unreadable)} unreadable/non-UTF-8 file(s), "
            "not scanned for re-inlined constants -- see --help's Honest limits.",
            file=sys.stderr,
        )
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--constants-file", required=True,
        help="Path to the single-source module defining the security-notice / "
             "delimiter string constants",
    )
    parser.add_argument(
        "--scan-root", required=True,
        help="Directory to scan for re-inlined copies of those constants",
    )
    args = parser.parse_args()

    constants_file = Path(args.constants_file)
    scan_root = Path(args.scan_root)
    if not scan_root.is_dir():
        print(f"ERROR: scan root not found: {scan_root}", file=sys.stderr)
        return 2

    constants = load_constants(constants_file)
    violations = find_reinlined_copies(constants, scan_root, constants_file)

    if violations:
        for v in violations:
            print(v)
        return 1
    print(f"OK -- no re-inlined copies of {len(constants)} constant(s) from {constants_file}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
