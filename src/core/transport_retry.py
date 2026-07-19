#!/usr/bin/env python3
"""
transport_retry.py

Retry wrapper for LLM provider calls. Transport level failures (connection
refused, timeout, HTTP 5xx, model not found) are provider problems, not model
output problems: they must be retried with backoff and, on exhaustion, surface
as a distinct UPSTREAM_UNAVAILABLE error instead of consuming validation gate
attempts as fake parse failures (improvement #7).
"""

import time
from typing import Callable, List, Optional


class ProviderTransportError(Exception):
    """The provider call kept failing at the transport level after retries."""

    def __init__(self, message: str, model: str = "", attempt_errors: Optional[List[str]] = None):
        super().__init__(message)
        self.model = model
        self.attempt_errors = attempt_errors or []


def call_with_transport_retry(
    fn: Callable[[], object],
    retries: int = 2,
    backoff: float = 2.0,
    model: str = "",
    sleep: Callable[[float], None] = time.sleep,
):
    """
    Calls ``fn``; on exception waits ``backoff * 2**n`` seconds and retries up
    to ``retries`` more times. Every attempt's provider message is kept so the
    failed payload can carry the full history in ``error.context``.
    """
    attempt_errors: List[str] = []
    total = max(retries, 0) + 1
    for attempt in range(total):
        try:
            return fn()
        except Exception as e:
            attempt_errors.append(f"{type(e).__name__}: {e}")
            if attempt + 1 < total:
                delay = backoff * (2**attempt)
                print(
                    f"[TransportRetry] Provider call failed (attempt "
                    f"{attempt + 1}/{total}): {e}. Retrying in {delay:.1f}s..."
                )
                sleep(delay)
    raise ProviderTransportError(
        f"Provider unavailable after {total} attempts: {attempt_errors[-1]}",
        model=model,
        attempt_errors=attempt_errors,
    )
