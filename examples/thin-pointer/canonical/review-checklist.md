# Canonical review checklist (single source of truth)

This file is the **only** full copy of this workflow. Runtime wrappers must
point here; they must not fork these steps into a second long prose tree.

1. Read the diff and the linked ADR (if any).
2. Check tests and lint for the touched package.
3. Verify secrets and PII did not enter the commit.
4. Confirm Change Summary / completion checklist when the change is non-trivial.
5. Approve or request changes with concrete file:line notes.

When the checklist changes, edit **this file only**, then rely on thin
pointers in each harness to pick up the same path.
