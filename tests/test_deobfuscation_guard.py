# -*- coding: utf-8 -*-
"""Regression test to ensure hyphen obfuscation patterns do not recur.

This guards against the lint-evasion patterns caught in issues.md Bug 1, 2, and 4
from recurring silently in the future.
"""

import pathlib

import pytest

# Repository root is two directories up from this test file
repo_root = pathlib.Path(__file__).resolve().parents[1]


def test_no_hyphen_obfuscation_in_scripts_and_src():
    """Scan all .py files in scripts/ and src/ for known hyphen obfuscation patterns."""
    scripts_dir = repo_root / "scripts"
    src_dir = repo_root / "src"

    bad_patterns = [
        "chr(45)",
        "chr(0x2d)",
        "\\x2d",
    ]
    
    directories_to_scan = [scripts_dir, src_dir]
    
    files_with_violations = []

    for directory in directories_to_scan:
        for py_file in directory.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                for pattern in bad_patterns:
                    if pattern in content:
                        files_with_violations.append((py_file.relative_to(repo_root), pattern))
            except Exception as e:
                pass # skip non-text or unreadable

    assert not files_with_violations, f"Found hyphen obfuscation patterns: {files_with_violations}"
