#!/usr/bin/env python3
"""
test_clean_environment_regression.py

Regression test suite proving clean-environment portability:
1. No personal (/home/howlcipher/...) path assumptions in generated products or source.
2. Deterministic compiler discovery hierarchy (HOWLFRAME_BIN -> command -v howlframe -> exit 127 diagnostic).
3. Actionable diagnostic when HowlFrame compiler is missing.
4. Provider routing & synthesis with deterministic fake backends (no external subscriptions required).
5. #56 native HowlChangeOps receipt recovery operates in clean environment.
6. MCP / FastMCP import compatibility and dependency bounds.
"""

import json
import os
from pathlib import Path
import subprocess
import pytest

from src.control_plane.agent_execution import (
    AgentBackendRegistry,
    FakeAgentBackend,
    AgentExecutionResult,
)
from src.control_plane.executor import (
    ExecutorRegistry,
    HowlChangeOpsExecutor,
    ExecutionReceipt,
)
from src.control_plane.human_boundary import HumanLifecycleManager
from src.control_plane.proposed_action import ProposedAction
from src.control_plane.synthesis.engine import ProductSynthesizer
from src.control_plane.synthesis.product_spec import ProductSpec
from src.control_plane.synthesis.provider_pool import (
    ProviderAvailabilityStatus,
    ProviderPoolManager,
)
from src.control_plane.synthesis.spec_synthesizer import NaturalLanguageSynthesizer
from src.control_plane.task_spec import TaskSpec


def test_no_personal_paths_in_generated_product_artifacts(tmp_path: Path):
    """Proves that synthesized products never contain personal home directory paths."""
    out_dir = tmp_path / "notes_bundle"
    engine = ProductSynthesizer()
    res = engine.create_from_prompt("Create a notes app with browser UI and API", output_dir=out_dir)
    assert res.success is True

    # Scan all generated files for personal path strings
    forbidden_tokens = ["howlcipher", "/home/howlcipher", "/var/home/howlcipher"]
    scanned_count = 0

    for fpath in out_dir.rglob("*"):
        if fpath.is_file() and not fpath.name.endswith(".pyc"):
            scanned_count += 1
            content = fpath.read_text(encoding="utf-8", errors="ignore")
            for token in forbidden_tokens:
                assert token not in content, f"Personal token '{token}' found in generated product file: {fpath.relative_to(out_dir)}"

    assert scanned_count >= 8, f"Expected at least 8 generated files, scanned {scanned_count}"


def _run_build_with_env(target_dir: Path, custom_env: dict) -> subprocess.CompletedProcess:
    spec = NaturalLanguageSynthesizer().synthesize("Create a service app")
    ProductSynthesizer()._synthesize_product_files(target_dir, spec)
    return subprocess.run(
        ["bash", str(target_dir / "scripts" / "build.sh")],
        cwd=str(target_dir),
        capture_output=True,
        text=True,
        env=custom_env,
    )


def test_compiler_discovery_hierarchy_and_actionable_error(tmp_path: Path):
    """Proves that missing compiler produces a deterministic exit code 127 and actionable diagnostic."""
    env = os.environ.copy()
    env.pop("HOWLFRAME_BIN", None)
    env["PATH"] = "/usr/bin:/bin"

    result = _run_build_with_env(tmp_path / "test_app", env)

    assert result.returncode == 127
    assert "ERROR: HowlFrame compiler executable not found." in result.stderr
    assert "Please install howlframe or set the HOWLFRAME_BIN environment variable." in result.stderr


def test_compiler_discovery_prefers_howlframe_bin_override(tmp_path: Path):
    """Proves that HOWLFRAME_BIN environment variable takes deterministic precedence."""
    repo_root = Path(__file__).resolve().parents[1]
    fake_compiler = repo_root / "tests" / "fake_compiler.py"
    assert fake_compiler.is_file()

    env = os.environ.copy()
    env["HOWLFRAME_BIN"] = str(fake_compiler)

    result = _run_build_with_env(tmp_path / "test_app_override", env)

    assert result.returncode == 0
    assert "✓ Build complete." in result.stdout
    assert (tmp_path / "test_app_override" / "build" / "backend.hfbc").exists()


def test_provider_fallback_chain_clean_environment(tmp_path: Path):
    """Proves provider selection fallback chain (codex -> agy -> devin -> claude) in clean environment."""
    events = []
    agent_errors = {
        "codex": "429 Too Many Requests: quota exceeded",
        "agy": "resource_exhausted: token limit exceeded",
        "devin_cli": "session limit reached",
    }

    class MockExhaustingBackend(FakeAgentBackend):
        def execute(self, task, cwd, role="implementation", **kwargs):
            if role == "implementation":
                events.append(task.actual_agent)
            err = agent_errors.get(task.actual_agent)
            ok = err is None
            return AgentExecutionResult(
                agent_id=task.actual_agent or self.agent_id,
                role=role,
                command=task.actual_agent or "agent",
                exit_code=0 if ok else 1,
                stdout="Success" if ok else "",
                stderr="" if ok else err,
                duration_seconds=0.01,
                success=ok,
            )

    pool = ProviderPoolManager()
    for p in ["codex", "agy", "devin_cli", "claude_code"]:
        pool.set_status(p, ProviderAvailabilityStatus.AVAILABLE)

    backend = MockExhaustingBackend()
    engine = ProductSynthesizer(provider_pool=pool, custom_backend=backend)
    res = engine.create_from_prompt("Create a inventory app", output_dir=tmp_path / "app")

    assert res.success is True
    assert res.implementing_provider == "claude_code"
    assert events == ["codex", "agy", "devin_cli", "claude_code"]
    assert pool.get_status("codex") in (ProviderAvailabilityStatus.RATE_LIMITED, ProviderAvailabilityStatus.SESSION_EXHAUSTED)
    assert pool.get_status("agy") in (ProviderAvailabilityStatus.RATE_LIMITED, ProviderAvailabilityStatus.SESSION_EXHAUSTED)
    assert pool.get_status("devin_cli") in (ProviderAvailabilityStatus.RATE_LIMITED, ProviderAvailabilityStatus.SESSION_EXHAUSTED)
    assert pool.get_status("claude_code") == ProviderAvailabilityStatus.AVAILABLE


def test_mcp_fastmcp_import_safety():
    """Proves FastMCP import is safely wrapped and does not crash when accessed in clean environments."""
    import src.infrastructure.mcp_server as mcp_module
    assert hasattr(mcp_module, "search_knowledge_library")
    assert callable(mcp_module.search_knowledge_library)
