#!/usr/bin/env python3
"""
agent_execution.py

Normalized execution abstraction for AI agents across implementation,
remediation, and review roles. Supports CLI backends, local execution,
and deterministic mock/fake backends for testing and CI.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import json, os, shlex, shutil, subprocess, time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from src.control_plane.task_spec import TaskSpec, DataClassSerializationMixin

AGENT_EXECUTION_SCHEMA_VERSION = "howlplane.agent_execution/v1"


class AgentExecutionError(RuntimeError):
    """Raised when an agent execution fails or encounters an unrecoverable error."""
    pass


class AgentUnavailableError(AgentExecutionError):
    """Raised when an explicitly requested agent backend is not installed or available."""
    pass


@dataclass
class AgentExecutionResult(DataClassSerializationMixin):
    """Normalized result of an agent execution invocation."""

    agent_id: str
    role: str
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    success: bool
    timed_out: bool = False
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema: str = AGENT_EXECUTION_SCHEMA_VERSION


class AgentBackend(ABC):
    """Abstract base class for all agent execution backends."""

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def execute(
        self,
        task: TaskSpec,
        cwd: Union[str, Path],
        role: str = "implementation",
        prompt_override: Optional[str] = None,
        timeout_seconds: int = 300,
        env_vars: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> AgentExecutionResult:
        pass


class SubprocessAgentBackend(AgentBackend):
    """Base backend for executing CLI agents via deterministic subprocess execution."""

    def __init__(
        self,
        agent_id: str,
        binary_name: str,
        cmd_builder: Optional[Callable[[TaskSpec, Path, str, str], List[str]]] = None,
    ):
        self.agent_id = agent_id
        self.binary_name = binary_name
        self._builder = cmd_builder

    def is_available(self) -> bool:
        return shutil.which(self.binary_name) is not None

    def build_command(self, task: TaskSpec, cwd: Path, role: str, prompt: str) -> List[str]:
        if self._builder:
            return self._builder(task, cwd, role, prompt)
        return [self.binary_name, prompt]

    def execute(
        self,
        task: TaskSpec,
        cwd: Union[str, Path],
        role: str = "implementation",
        prompt_override: Optional[str] = None,
        timeout_seconds: int = 300,
        env_vars: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> AgentExecutionResult:
        target_cwd = Path(cwd).resolve()
        if not self.is_available():
            return AgentExecutionResult(
                agent_id=self.agent_id,
                role=role,
                command=self.binary_name,
                exit_code=127,
                stdout="",
                stderr=f"Agent binary '{self.binary_name}' is not installed or available on PATH.",
                duration_seconds=0.0,
                success=False,
                error_message=f"Agent '{self.agent_id}' unavailable",
            )

        prompt = prompt_override or f"Execute task {task.task_id}: {task.objective}"
        cmd_args = self.build_command(task, target_cwd, role, prompt)
        cmd_str = " ".join(shlex.quote(c) for c in cmd_args)

        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)

        start_t = time.time()
        try:
            completed = subprocess.run(
                args=cmd_args,
                cwd=str(target_cwd),
                capture_output=True,
                text=True,
                env=env,
                timeout=timeout_seconds,
            )
            elapsed = round(time.time() - start_t, 3)
            return AgentExecutionResult(
                agent_id=self.agent_id,
                role=role,
                command=cmd_str,
                exit_code=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                duration_seconds=elapsed,
                success=(completed.returncode == 0),
                error_message=None if completed.returncode == 0 else f"Process exited with code {completed.returncode}",
            )
        except subprocess.TimeoutExpired as exc:
            dur = round(time.time() - start_t, 3)
            out = exc.stdout.decode("utf-8", errors="replace") if exc.stdout else ""
            err = exc.stderr.decode("utf-8", errors="replace") if exc.stderr else ""
            return AgentExecutionResult(
                agent_id=self.agent_id,
                role=role,
                command=cmd_str,
                exit_code=-1,
                stdout=out,
                stderr=err + f"\nTimeout after {timeout_seconds}s.",
                duration_seconds=dur,
                success=False,
                timed_out=True,
                error_message=f"Timeout after {timeout_seconds}s",
            )
        except Exception as exc:
            dur = round(time.time() - start_t, 3)
            return AgentExecutionResult(
                agent_id=self.agent_id,
                role=role,
                command=cmd_str,
                exit_code=-1,
                stdout="",
                stderr=str(exc),
                duration_seconds=dur,
                success=False,
                error_message=str(exc),
            )


# Built-in specialized CLI agent backend instances
class ClaudeCodeBackend(SubprocessAgentBackend):
    def __init__(self):
        super().__init__("claude_code", "claude", lambda t, c, r, p: ["claude", "-p", p])


class CodexBackend(SubprocessAgentBackend):
    def __init__(self):
        super().__init__("codex", "codex", lambda t, c, r, p: ["codex", p])


class GeminiCLIBackend(SubprocessAgentBackend):
    def __init__(self):
        super().__init__("gemini_cli", "gemini", lambda t, c, r, p: ["gemini", "-p", p])


class AgyBackend(SubprocessAgentBackend):
    def __init__(self):
        super().__init__("agy", "agy", lambda t, c, r, p: ["agy", "-p", p, "--mode", "accept-edits"])


class DevinCLIBackend(SubprocessAgentBackend):
    def __init__(self):
        def _devin_cmd(t, c, r, p):
            tf = c / ".task_runs" / t.task_id / "task.yaml"
            return ["devin", "run", "--task-file", str(tf)] if tf.exists() else ["devin", "run", "--task", p]
        super().__init__("devin_cli", "devin", _devin_cmd)


class LocalOllamaBackend(SubprocessAgentBackend):
    def __init__(self, model: str = "qwen2.5-coder:32b"):
        super().__init__("local_ollama", "ollama", lambda t, c, r, p: ["ollama", "run", model, p])


class FakeAgentBackend(AgentBackend):
    """Deterministic programmable agent backend for automated tests and CI fixtures."""

    def __init__(
        self,
        agent_id: str = "fake_agent",
        default_exit_code: int = 0,
        default_stdout: str = "Fake implementation completed successfully.",
        default_stderr: str = "",
        side_effect: Optional[Callable[[TaskSpec, Path, str], None]] = None,
        duration: float = 0.05,
    ):
        self.agent_id = agent_id
        self.default_exit_code = default_exit_code
        self.default_stdout = default_stdout
        self.default_stderr = default_stderr
        self.side_effect = side_effect
        self.duration = duration
        self.executed_calls: List[Dict[str, Any]] = []

    def is_available(self) -> bool:
        return True

    def execute(
        self,
        task: TaskSpec,
        cwd: Union[str, Path],
        role: str = "implementation",
        prompt_override: Optional[str] = None,
        timeout_seconds: int = 300,
        env_vars: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> AgentExecutionResult:
        target_cwd = Path(cwd).resolve()
        prompt = prompt_override or f"Fake execute: {task.objective}"
        self.executed_calls.append({
            "task_id": task.task_id,
            "role": role,
            "prompt": prompt,
            "cwd": str(target_cwd),
        })

        if self.side_effect:
            try:
                self.side_effect(task, target_cwd, prompt)
            except Exception as exc:
                return AgentExecutionResult(
                    agent_id=self.agent_id,
                    role=role,
                    command=f"fake_agent({self.agent_id})",
                    exit_code=1,
                    stdout="",
                    stderr=f"Side effect error: {exc}",
                    duration_seconds=self.duration,
                    success=False,
                    error_message=str(exc),
                )

        ok = (self.default_exit_code == 0)
        return AgentExecutionResult(
            agent_id=self.agent_id,
            role=role,
            command=f"fake_agent({self.agent_id})",
            exit_code=self.default_exit_code,
            stdout=self.default_stdout,
            stderr=self.default_stderr,
            duration_seconds=self.duration,
            success=ok,
            error_message=None if ok else f"Exit code {self.default_exit_code}",
        )


class AgentBackendRegistry:
    """Registry providing backend instances by agent_id."""

    _instances: Dict[str, AgentBackend] = {
        "claude_code": ClaudeCodeBackend(),
        "codex": CodexBackend(),
        "gemini_cli": GeminiCLIBackend(),
        "agy": AgyBackend(),
        "devin_cli": DevinCLIBackend(),
        "local_ollama": LocalOllamaBackend(),
    }

    @classmethod
    def get_backend(cls, agent_id: str, custom_backend: Optional[AgentBackend] = None) -> AgentBackend:
        if custom_backend is not None:
            return custom_backend
        if agent_id in cls._instances:
            return cls._instances[agent_id]
        return SubprocessAgentBackend(agent_id=agent_id, binary_name=agent_id)

    @classmethod
    def register_backend(cls, agent_id: str, backend: AgentBackend) -> None:
        cls._instances[agent_id] = backend
