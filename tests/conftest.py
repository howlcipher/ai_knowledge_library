import pytest
from src.core.orchestrator import Orchestrator

@pytest.fixture
def orchestrator_factory():
    """Factory fixture providing Orchestrator instances with automatic shutdown.

    Each test can call ``orchestrator_factory()`` to create a new ``Orchestrator``.
    All created instances are shut down after the test completes.
    """
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
