#!/usr/bin/env python3
"""
claude_code_backend.py

Alternative payload-pipeline tier backend that shells out to headless Claude
Code (`claude -p ... --output-format json`) instead of routing through
LiteLLM, so a tier can be judged by the Claude Pro subscription instead of an
API-keyed provider (improvements.md item 20). Selected when a tier's
resolved model equals CLAUDE_CODE_MODEL.
"""

import json
import subprocess
from types import SimpleNamespace
from typing import Optional

CLAUDE_CODE_MODEL = "claude_code"


class ClaudeCodeAgent:
    """Drop-in replacement for orchestrator.Agent: same
    generate_response(user_prompt, context="", raise_errors=False) contract,
    returning an object with a .content attribute on success, backed by the
    `claude` CLI instead of litellm.completion.
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        model: str = CLAUDE_CODE_MODEL,
        tools: list = None,
        timeout: Optional[float] = None,
        response_format: Optional[dict] = None,
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.timeout = timeout
        # The claude CLI has no LiteLLM-style response_format/schema
        # enforcement; fold the schema into the prompt as an instruction
        # instead so callers built for a structured-outputs Agent degrade
        # gracefully rather than erroring on an unsupported kwarg.
        self.response_format = response_format

    def generate_response(
        self, user_prompt: str, context: str = "", raise_errors: bool = False
    ):
        full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
        if context:
            full_prompt += f"\n\nContext:\n{context}"
        if self.response_format:
            schema = (self.response_format or {}).get("json_schema", {}).get("schema")
            if schema:
                full_prompt += (
                    "\n\nRespond with bare JSON only, conforming exactly to "
                    f"this JSON schema:\n{json.dumps(schema)}"
                )

        cmd = [
            "claude",
            "-p",
            full_prompt,
            "--output-format",
            "json",
            "--max-turns",
            "1",
        ]

        print(f"[{self.name}] Thinking (Claude Code)...")
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired as e:
            print(f"[{self.name}] Claude Code timed out: {e}")
            if raise_errors:
                raise
            return None
        except FileNotFoundError as e:
            print(f"[{self.name}] Claude Code CLI not found: {e}")
            if raise_errors:
                raise
            return None

        if proc.returncode != 0:
            err = f"claude exited {proc.returncode}: {proc.stderr.strip()[:500]}"
            print(f"[{self.name}] {err}")
            if raise_errors:
                raise RuntimeError(err)
            return None

        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError as e:
            print(f"[{self.name}] Failed to parse Claude Code JSON output: {e}")
            if raise_errors:
                raise
            return None

        if data.get("is_error"):
            err = f"Claude Code reported an error: {data.get('result') or data}"
            print(f"[{self.name}] {err}")
            if raise_errors:
                raise RuntimeError(err)
            return None

        return SimpleNamespace(content=data.get("result", ""))
