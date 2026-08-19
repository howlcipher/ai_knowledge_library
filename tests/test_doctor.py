"""
test_doctor.py

Unit tests for src/infrastructure/doctor.py diagnostics.
"""

from pathlib import Path
from src.infrastructure.doctor import (
    check_python_environment,
    check_dependencies,
    check_go_toolchain,
    check_git_status,
    check_control_plane_ledger,
    run_diagnostics,
    main as doctor_main,
)


def test_check_python_environment(monkeypatch):
    monkeypatch.setenv("VIRTUAL_ENV", "/fake/venv")
    check = check_python_environment()
    assert check.status == "ok"
    assert "fake/venv" in check.message

    monkeypatch.delenv("VIRTUAL_ENV", raising=False)
    check_no_venv = check_python_environment()
    assert check_no_venv.status == "warning"


def test_check_dependencies():
    check = check_dependencies()
    assert check.status == "ok"


def test_check_go_toolchain():
    check = check_go_toolchain()
    assert check.status in ("ok", "warning")


def test_check_git_status(tmp_path):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    check = check_git_status(tmp_path)
    assert check.status == "ok"

    non_git = tmp_path / "empty_dir"
    non_git.mkdir()
    check_bad = check_git_status(non_git)
    assert check_bad.status == "warning"


def test_check_control_plane_ledger(tmp_path):
    check_empty = check_control_plane_ledger(tmp_path)
    assert check_empty.status == "ok"

    logs_dir = tmp_path / "logs" / "control_plane"
    logs_dir.mkdir(parents=True)
    ledger_file = logs_dir / "evidence_ledger.jsonl"
    ledger_file.write_text('{"task_id": "T1"}\n{"task_id": "T2"}\n', encoding="utf-8")

    check_valid = check_control_plane_ledger(tmp_path)
    assert check_valid.status == "ok"
    assert "2 valid" in check_valid.message


def test_run_diagnostics():
    checks = run_diagnostics()
    assert len(checks) == 5
    assert all(c.status in ("ok", "warning") for c in checks)


def test_doctor_main():
    code = doctor_main()
    assert code in (0, 1)
