#!/usr/bin/env python3
"""
locking.py

Lightweight filesystem repository and task lifecycle locks for HowlPlane.
Prevents concurrent mutation workflows from destroying git attribution or racing reviews,
and protects task lifecycle operations against concurrent invocation.
Provides safe stale lock detection without requiring Redis, daemons, or databases.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import errno
import os
from pathlib import Path
import socket
import time
from typing import Any, Dict, Optional, Tuple, Type, Union

from src.control_plane.atomic_io import safe_load_json
from src.control_plane.task_spec import DataClassSerializationMixin

LOCK_SCHEMA_VERSION = "howlplane.lock/v1"


class LockError(RuntimeError):
    """Base exception for locking errors."""
    pass


class RepositoryLockedError(LockError):
    """Raised when repository mutation is blocked because another active task holds the repository lock."""
    pass


class TaskLockedError(LockError):
    """Raised when task lifecycle mutation is blocked because another operation holds the task lock."""
    pass


@dataclass
class LockMetadata(DataClassSerializationMixin):
    """Structured metadata stored inside a lock file."""

    task_id: str
    pid: int
    hostname: str
    lock_type: str  # "repository_mutation" | "task_run"
    operation: str = "work"
    command: str = "ai"
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    process_create_time: float = 0.0
    schema: str = LOCK_SCHEMA_VERSION


def get_process_create_time(pid: int) -> float:
    """Extracts process creation timestamp on Linux /proc or falls back to current time."""
    try:
        stat_path = Path(f"/proc/{pid}/stat")
        if stat_path.is_file():
            return stat_path.stat().st_mtime
    except Exception:
        pass
    return time.time()


def is_process_alive(
    pid: int,
    hostname: str,
    expected_create_time: Optional[float] = None,
) -> Tuple[bool, str]:
    """
    Deterministically checks if a process with `pid` is actively running on `hostname`.
    Returns (is_alive, reason).
    """
    current_host = socket.gethostname()
    if hostname != current_host:
        return True, f"Process is on different host '{hostname}' (current: '{current_host}')"

    if pid <= 0:
        return False, "Invalid PID <= 0"

    try:
        os.kill(pid, 0)
    except OSError as err:
        if err.errno == errno.ESRCH:
            return False, f"Process PID {pid} is no longer running (ESRCH)"
        elif err.errno == errno.EPERM:
            return True, f"Process PID {pid} is running under another user account"
        else:
            return True, f"Process check returned unexpected OSError {err}"

    if expected_create_time and expected_create_time > 0:
        actual_create_time = get_process_create_time(pid)
        if abs(actual_create_time - expected_create_time) > 10.0:
            return False, f"PID {pid} was recycled by operating system (mismatched start time)"

    return True, f"Process PID {pid} is actively running"


def get_repo_lock_path(repo_root: Union[str, Path]) -> Path:
    """Determines the canonical lock path for repository mutations."""
    root = Path(repo_root).resolve()
    git_dir = root / ".git"
    if git_dir.is_dir():
        return git_dir / "howlplane.lock"
    task_runs = root / ".task_runs"
    task_runs.mkdir(parents=True, exist_ok=True)
    return task_runs / ".repo.lock"


def get_task_lock_path(repo_root: Union[str, Path], task_id: str) -> Path:
    """Determines the canonical lock path for a specific task lifecycle run."""
    root = Path(repo_root).resolve()
    task_dir = root / ".task_runs" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    return task_dir / ".task.lock"


class _BaseFileLock:
    """Base mutual-exclusion file lock with stale process reclamation."""

    lock_type = "generic_lock"
    error_cls: Type[LockError] = LockError

    def __init__(
        self,
        repo_root: Union[str, Path],
        task_id: str,
        lock_path: Path,
        command: str,
        operation: str,
    ):
        self.repo_root = Path(repo_root).resolve()
        self.task_id = task_id
        self.lock_path = lock_path
        self.command = command
        self.operation = operation
        self._acquired = False

    def acquire(self) -> bool:
        my_pid = os.getpid()
        my_host = socket.gethostname()
        my_ctime = get_process_create_time(my_pid)

        if self.lock_path.exists():
            try:
                data = safe_load_json(self.lock_path)
                existing = LockMetadata.from_dict(data)
            except Exception:
                existing = None

            if existing:
                if existing.pid == my_pid and existing.hostname == my_host:
                    if self._acquired:
                        return True
                    raise self.error_cls(
                        f"{self.lock_type.replace('_', ' ').title()} lock already held on task '{existing.task_id}'."
                    )

                alive, reason = is_process_alive(
                    existing.pid, existing.hostname, existing.process_create_time
                )
                if alive:
                    raise self.error_cls(
                        f"{self.lock_type.replace('_', ' ').title()} lock held by active process "
                        f"PID {existing.pid} ({existing.command}) for task '{existing.task_id}' "
                        f"started at {existing.started_at}. Concurrent operation blocked."
                    )
                else:
                    try:
                        self.lock_path.unlink()
                    except Exception:
                        pass
            else:
                try:
                    self.lock_path.unlink()
                except Exception:
                    pass

        meta = LockMetadata(
            task_id=self.task_id,
            pid=my_pid,
            hostname=my_host,
            lock_type=self.lock_type,
            operation=self.operation,
            command=self.command,
            process_create_time=my_ctime,
        )

        content = meta.to_json()
        try:
            self.lock_path.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(
                str(self.lock_path),
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o644,
            )
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
            self._acquired = True
            return True
        except FileExistsError:
            raise self.error_cls(
                f"Contention on '{self.lock_path}'. Another operation acquired the lock concurrently."
            )

    def release(self) -> None:
        if not self._acquired:
            return
        my_pid = os.getpid()
        my_host = socket.gethostname()
        if self.lock_path.exists():
            try:
                data = safe_load_json(self.lock_path)
                existing = LockMetadata.from_dict(data)
                if existing.pid == my_pid and existing.hostname == my_host:
                    self.lock_path.unlink()
            except Exception:
                try:
                    self.lock_path.unlink()
                except Exception:
                    pass
        self._acquired = False

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


class RepoLock(_BaseFileLock):
    """
    Mutual-exclusion lock for repository mutations.
    Ensures only one mutating task modifies a working tree at a time.
    """

    lock_type = "repository_mutation"
    error_cls = RepositoryLockedError

    def __init__(
        self,
        repo_root: Union[str, Path],
        task_id: str,
        command: str = "ai work --execute",
        operation: str = "repository_mutation",
    ):
        path = get_repo_lock_path(repo_root)
        super().__init__(repo_root, task_id, path, command, operation)


class TaskLock(_BaseFileLock):
    """
    Mutual-exclusion lock for a single task's lifecycle operations
    (approve, reject, resume, cancel, bounded execution).
    """

    lock_type = "task_run"
    error_cls = TaskLockedError

    def __init__(
        self,
        repo_root: Union[str, Path],
        task_id: str,
        operation: str = "resume",
        command: str = "ai resume",
    ):
        path = get_task_lock_path(repo_root, task_id)
        super().__init__(repo_root, task_id, path, command, operation)


class LocalInferenceBusyError(LockError):
    """Raised when a second local model inference is attempted while one is already running."""
    pass


def get_local_inference_lock_path(repo_root: Union[str, Path]) -> Path:
    """Canonical machine-wide lock path enforcing a single concurrent local inference."""
    root = Path(repo_root).resolve()
    task_runs = root / ".task_runs"
    task_runs.mkdir(parents=True, exist_ok=True)
    return task_runs / ".local_inference.lock"


class LocalInferenceLock(_BaseFileLock):
    """
    Machine-wide mutual-exclusion lock enforcing exactly one concurrent local
    (Ollama) model inference at a time, regardless of how many HowlPlane
    processes are running (#58 Phase 7). HowlPlane's own lock is authoritative
    and does not rely solely on Ollama's own internal queuing behavior.
    """

    lock_type = "local_inference"
    error_cls = LocalInferenceBusyError

    def __init__(
        self,
        repo_root: Union[str, Path],
        task_id: str,
        command: str = "ollama_local",
    ):
        path = get_local_inference_lock_path(repo_root)
        super().__init__(repo_root, task_id, path, command, "local_inference")
