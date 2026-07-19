#!/usr/bin/env python3
"""Select and run the tests relevant to the current git change set.

Maps changed Python sources to test files in tests/ that reference the
module by name, includes changed test files directly, and falls back to
the full suite when broad-surface files change. Changed sources with no
matching test are reported as coverage gaps.

Usage:
    python scripts/select_relevant_tests.py            # select and run
    python scripts/select_relevant_tests.py --list     # selection only
    python scripts/select_relevant_tests.py --base REF # diff against REF
    python scripts/select_relevant_tests.py --strict   # fail on gaps
"""

import argparse
import re
import subprocess  # nosec B404
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = REPO_ROOT / "tests"

# Changes here affect behavior suite-wide; run everything.
FULL_SUITE_TRIGGERS = (
    "Makefile",
    "pyproject.toml",
    "conftest.py",
    "config/",
    ".github/workflows/",
)

def run_git(*args: str) -> str:
    result = subprocess.run(  # nosec B603 B607
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    )
    return result.stdout


def changed_files(base: str | None = None) -> list[str]:
    """Repo-relative changed paths: vs HEAD plus untracked, or vs a base ref."""
    if base:
        files = set(run_git("diff", "--name-only", f"{base}...HEAD").split())
    else:
        files = set(run_git("diff", "--name-only", "HEAD").split())
        files |= set(run_git("ls-files", "--others", "--exclude-standard").split())
    return sorted(files)


def module_names(path: str) -> set[str]:
    """Names a test file would use to reference this source file."""
    parts = list(Path(path).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    if not parts:
        return set()
    names = {parts[-1], ".".join(parts)}
    if parts[0] in ("src", "scripts") and len(parts) > 1:
        names.add(".".join(parts[1:]))
    return names


def select_tests(changed: list[str], test_sources: dict[str, str]):
    """Return (selected test paths, uncovered sources, full-suite trigger or None).

    test_sources maps repo-relative test paths to their file contents.
    """
    selected: set[str] = set()
    uncovered: list[str] = []
    trigger = None
    for path in changed:
        if any(
            path == t or (t.endswith("/") and path.startswith(t))
            for t in FULL_SUITE_TRIGGERS
        ):
            trigger = trigger or path
            continue
        if path.endswith(".go") or path in ("go.mod", "go.sum"):
            trigger = trigger or path
            continue
        if path.startswith("tests/") and path.endswith(".py"):
            selected.add(path)
            continue
        if not path.endswith(".py"):
            continue
        names = module_names(path)
        patterns = [re.compile(rf"\b{re.escape(n)}\b") for n in names]
        hits = [
            test
            for test, text in test_sources.items()
            if any(p.search(text) for p in patterns)
        ]
        if hits:
            selected.update(hits)
        else:
            uncovered.append(path)
    return sorted(selected), uncovered, trigger


def load_test_sources() -> dict[str, str]:
    return {
        str(p.relative_to(REPO_ROOT)): p.read_text(encoding="utf-8", errors="replace")
        for p in sorted(TESTS_DIR.glob("test_*.py"))
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="diff against this ref instead of the working tree")
    parser.add_argument("--list", action="store_true", help="print selection, do not run")
    parser.add_argument("--strict", action="store_true", help="exit 1 if a changed source has no matching test")
    args = parser.parse_args()

    changed = changed_files(args.base)
    if not changed:
        print("No changes detected; nothing to run.")
        return 0

    selected, uncovered, trigger = select_tests(changed, load_test_sources())

    if uncovered:
        print("WARNING: changed sources with no matching test (protocol step 7 gap):")
        for path in uncovered:
            print(f"  {path}")

    if trigger:
        print(f"Broad-surface change ({trigger}); running the full suite.")
        pytest_args = ["tests/"]
    elif selected:
        print("Relevant tests:")
        for path in selected:
            print(f"  {path}")
        pytest_args = selected
    else:
        print("No relevant Python tests for this change set.")
        return 1 if (args.strict and uncovered) else 0

    if args.list:
        return 1 if (args.strict and uncovered) else 0

    rc = subprocess.call(  # nosec B603
        [sys.executable, "-m", "pytest", "-v", *pytest_args], cwd=REPO_ROOT
    )
    if rc == 0 and args.strict and uncovered:
        return 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
