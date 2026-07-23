"""Tests for SyncMCPClient's connect timeout. Without a bound here, a
missing binary or a hung MCP server subprocess blocks Orchestrator
construction (and anything that depends on it, including the test suite)
forever: `future.result()` had no timeout at all before this fix."""

import asyncio
import time

import pytest

from src.core.mcp_client import DEFAULT_MCP_TIMEOUT, SyncMCPClient


def test_connect_raises_timeout_error_on_hanging_server():
    client = SyncMCPClient(name="hangs", command="true", args=[])

    async def _hang():
        await asyncio.sleep(5)

    client._initialize = _hang

    start = time.time()
    with pytest.raises(TimeoutError, match="hangs"):
        client.connect(timeout=0.2)
    elapsed = time.time() - start
    assert elapsed < 2.0, f"connect() should fail fast, took {elapsed:.1f}s"

    client._thread.join(timeout=1.0)
    assert not client._thread.is_alive(), "background loop must stop after a timed-out connect"


def test_connect_succeeds_within_timeout():
    client = SyncMCPClient(name="fast", command="true", args=[])

    async def _quick():
        return None

    client._initialize = _quick
    client.connect(timeout=5.0)  # must not raise

    client.close(timeout=1.0)


def test_default_timeout_is_finite():
    assert 0 < DEFAULT_MCP_TIMEOUT < float("inf")
