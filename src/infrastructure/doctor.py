#!/usr/bin/env python3
"""
doctor.py

System environment, dependency, and toolchain health diagnostics for ai_knowledge_library.
Checks:
- Python interpreter & active virtualenv
- Essential Python package dependencies (pytest, yaml, jsonschema)
- Go toolchain availability (go binary and version)
- Git repository status and hooks
- Control plane evidence ledger integrity
"""

from dataclasses import dataclass
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Dict, List, Optional


@dataclass
class DiagnosticCheck:
    name: str
    status: str  # "ok", "warning", "error"
    message: str
    details: Optional[Dict[str, str]] = None


def check_python_environment() -> DiagnosticCheck:
    venv = os.environ.get("VIRTUAL_ENV")
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if venv:
        return DiagnosticCheck(
            name="Python Environment",
            status="ok",
            message=f"Running in virtual environment: {venv} (Python {py_ver})",
        )
    return DiagnosticCheck(
        name="Python Environment",
        status="warning",
        message=f"Not running inside an active VIRTUAL_ENV (Python {py_ver})",
    )


def check_dependencies() -> DiagnosticCheck:
    required = ["pytest", "yaml", "jsonschema"]
    missing = []
    for pkg in required:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        return DiagnosticCheck(
            name="Python Dependencies",
            status="error",
            message=f"Missing required dependencies: {', '.join(missing)}",
        )
    return DiagnosticCheck(
        name="Python Dependencies",
        status="ok",
        message="All required dependencies (pytest, yaml, jsonschema) are importable.",
    )


def check_go_toolchain() -> DiagnosticCheck:
    go_path = shutil.which("go")
    if not go_path:
        return DiagnosticCheck(
            name="Go Toolchain",
            status="warning",
            message="Go compiler ('go') not found in PATH.",
        )
    try:
        res = subprocess.run([go_path, "version"], capture_output=True, text=True, check=True)
        return DiagnosticCheck(
            name="Go Toolchain",
            status="ok",
            message=f"Go toolchain detected: {res.stdout.strip()}",
        )
    except Exception as exc:
        return DiagnosticCheck(
            name="Go Toolchain",
            status="warning",
            message=f"Go binary found at {go_path} but failed to query version: {exc}",
        )


def check_git_status(repo_root: Path) -> DiagnosticCheck:
    if not (repo_root / ".git").is_dir():
        return DiagnosticCheck(
            name="Git Repository",
            status="warning",
            message=f"Directory {repo_root} is not a git repository.",
        )
    return DiagnosticCheck(
        name="Git Repository",
        status="ok",
        message=f"Valid git repository confirmed at {repo_root}.",
    )


def check_control_plane_ledger(repo_root: Path) -> DiagnosticCheck:
    ledger_file = repo_root / "logs" / "control_plane" / "evidence_ledger.jsonl"
    if not ledger_file.exists():
        return DiagnosticCheck(
            name="Evidence Ledger",
            status="ok",
            message="No evidence ledger log file exists yet (clean state).",
        )
    try:
        valid_lines = 0
        with open(ledger_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    json.loads(line)
                    valid_lines += 1
        return DiagnosticCheck(
            name="Evidence Ledger",
            status="ok",
            message=f"Evidence ledger healthy ({valid_lines} valid JSON records).",
        )
    except Exception as exc:
        return DiagnosticCheck(
            name="Evidence Ledger",
            status="error",
            message=f"Evidence ledger file is corrupted: {exc}",
        )


def run_diagnostics(repo_root: Optional[Path] = None) -> List[DiagnosticCheck]:
    root = repo_root or Path(__file__).resolve().parent.parent.parent
    return [
        check_python_environment(),
        check_dependencies(),
        check_go_toolchain(),
        check_git_status(root),
        check_control_plane_ledger(root),
    ]


def main() -> int:
    print("=" * 60)
    print("AI Knowledge Library - System & Toolchain Diagnostics")
    print("=" * 60)
    checks = run_diagnostics()
    has_error = False
    for check in checks:
        if check.status == "ok":
            symbol = "✓"
        elif check.status == "warning":
            symbol = "!"
        else:
            symbol = "✗"
            has_error = True
        print(f"[{symbol}] {check.name}: {check.message}")
    print("=" * 60)
    return 1 if has_error else 0


if __name__ == "__main__":
    sys.exit(main())
