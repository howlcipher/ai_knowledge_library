import os
from pathlib import Path
import shutil
import pytest


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """
    Ensures deterministic compiler discovery and fake agent availability
    for all unit, synthesis, and CLI tests across clean CI and local environments.
    """
    repo_root = Path(__file__).resolve().parents[1]
    fake_compiler = repo_root / "tests" / "fake_compiler.py"

    # If HOWLFRAME_BIN is not set and howlframe is not on PATH, point to fake_compiler
    if not os.environ.get("HOWLFRAME_BIN") and not shutil.which("howlframe"):
        if fake_compiler.is_file():
            monkeypatch.setenv("HOWLFRAME_BIN", str(fake_compiler))

    # In automated test runs, set deterministic baseline mode unless live providers requested
    if not os.environ.get("HOWLPLANE_LIVE_PROVIDERS") and not os.environ.get("HOWLPLANE_SYNTHESIS_MODE"):
        monkeypatch.setenv("HOWLPLANE_SYNTHESIS_MODE", "deterministic_baseline")


@pytest.fixture
def orchestrator_factory():
    """Factory fixture providing Orchestrator instances with automatic shutdown.

    Each test can call ``orchestrator_factory()`` to create a new ``Orchestrator``.
    All created instances are shut down after the test completes.
    """
    from src.core.orchestrator import Orchestrator
    created = []

    def _make(*args, **kwargs):
        instance = Orchestrator(*args, **kwargs)
        created.append(instance)
        return instance

    yield _make

    # Teardown: shut down all created orchestrators
    for orchestrator in created:
        try:
            orchestrator.shutdown()
        except Exception:
            # Suppress shutdown errors to avoid test failures
            pass
