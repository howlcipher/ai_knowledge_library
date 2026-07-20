#!/usr/bin/env python3
"""
provider_preflight.py

Fail-fast provider checks run before pass 1 of the payload pipeline
(improvements.md item 5). A crashed Ollama server or a removed model tag
previously burned all three validation attempts and surfaced as a bogus
`validation_gate.parse` failure; these checks catch that class of problem
up front with an actionable message instead.

Per model the preflight verifies, in order:

1. For Ollama backed models: the server answers `/api/tags` and the
   configured tag is present in the response.
2. A one token generation succeeds, proving the model actually loads
   (a 30B tag can be listed yet still crash the server on load).
"""

import json
import os
import shutil
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import List, Optional

import litellm

from src.core.claude_code_backend import CLAUDE_CODE_MODEL

OLLAMA_PREFIXES = ("ollama/", "ollama_chat/")
DEFAULT_OLLAMA_BASE = "http://localhost:11434"


@dataclass
class PreflightResult:
    ok: bool
    checked_models: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def ollama_base_url() -> str:
    """Ollama endpoint, honoring the same env override LiteLLM uses."""
    base = os.environ.get("OLLAMA_API_BASE") or DEFAULT_OLLAMA_BASE
    return base.rstrip("/")


def _ollama_tag(model: str) -> str:
    """'ollama/qwen3:30b-instruct' -> 'qwen3:30b-instruct'."""
    return model.split("/", 1)[1]


def _check_ollama_tag(model: str, timeout: float) -> Optional[str]:
    """Verifies the Ollama server is up and serves the model's tag."""
    base = ollama_base_url()
    tag = _ollama_tag(model)
    try:
        with urllib.request.urlopen(  # nosec B310 - fixed http(s) endpoint
            f"{base}/api/tags", timeout=timeout
        ) as response:
            data = json.load(response)
    except (urllib.error.URLError, OSError, ValueError) as e:
        return (
            f"Ollama server unreachable at {base} ({e}). "
            "Start it with `ollama serve` or fix OLLAMA_API_BASE."
        )

    available = [m.get("name", "") for m in data.get("models", [])]
    # Ollama resolves a bare tag to ':latest'.
    if tag in available or f"{tag}:latest" in available:
        return None
    return (
        f"Model tag '{tag}' not found on Ollama server at {base}. "
        f"Available tags: {', '.join(available) or 'none'}. "
        f"Pull it with `ollama pull {tag}`."
    )


def _check_claude_code_cli() -> Optional[str]:
    """Verifies the `claude` CLI binary is on PATH. No generation ping is
    sent — invoking headless Claude Code costs real session usage, unlike a
    one token LiteLLM ping, so preflight only checks reachability."""
    if shutil.which("claude") is None:
        return (
            "The 'claude' CLI was not found on PATH, required for the "
            "claude_code tier backend. Install Claude Code and ensure "
            "`claude` is on PATH, or change tier_models to a LiteLLM model."
        )
    return None


def _check_generation(model: str, timeout: float) -> Optional[str]:
    """One token generation proving the provider accepts the model."""
    try:
        litellm.completion(
            model=model,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1,
            timeout=timeout,
        )
    except Exception as e:
        return f"One token preflight generation failed for '{model}': {e}"
    return None


def preflight_models(models: List[str], timeout: float = 120.0) -> PreflightResult:
    """
    Checks every distinct model once, collecting all failures so a run with
    two broken tiers reports both instead of the first. The generous default
    timeout covers cold loading a large local model into RAM, which also
    leaves it warm for pass 1.
    """
    result = PreflightResult(ok=True)
    for model in dict.fromkeys(models):
        result.checked_models.append(model)
        if model.startswith(OLLAMA_PREFIXES):
            error = _check_ollama_tag(model, timeout=min(timeout, 10.0))
            if error:
                # Server or tag is broken; a generation attempt adds nothing.
                result.errors.append(error)
                result.ok = False
                continue
        if model == CLAUDE_CODE_MODEL:
            error = _check_claude_code_cli()
        else:
            error = _check_generation(model, timeout=timeout)
        if error:
            result.errors.append(error)
            result.ok = False
    return result
