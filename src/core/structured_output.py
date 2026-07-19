#!/usr/bin/env python3
"""
structured_output.py

Builds the LiteLLM ``response_format`` for provider enforced structured
outputs in the payload pipeline (documentation/multi_agent_payload_protocol.md,
Additional Recommendation 1). Passing the AgentTaskPayload JSON schema to the
provider makes schema compliance mechanical (Ollama compiles it into a
decoding grammar; OpenAI and Gemini enforce it server side) instead of relying
on prompt discipline alone. The validation gate remains the authority: the
provider constraint is defense in depth, not a replacement for the gate.
"""

import json
import os
from typing import Optional

from src.infrastructure.config_loader import default_loader

# Keys that are schema metadata, not constraints. Some providers reject
# unknown top level keywords, and none of them need these to enforce shape.
_METADATA_KEYS = ("$schema", "$id")


def default_schema_path() -> str:
    return os.path.join(
        default_loader.get_repo_root(),
        "config",
        "schemas",
        "agent_task_payload.schema.json",
    )


def payload_response_format(schema_path: Optional[str] = None) -> dict:
    """
    Returns the ``response_format`` dict for ``litellm.completion`` carrying
    the AgentTaskPayload schema. ``strict`` is False because the schema has
    optional fields at every level, which OpenAI strict mode rejects; Ollama
    ignores the flag and always constrains decoding to the schema.
    """
    with open(schema_path or default_schema_path(), "r", encoding="utf8") as f:
        schema = json.load(f)
    for key in _METADATA_KEYS:
        schema.pop(key, None)
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "agent_task_payload",
            "schema": schema,
            "strict": False,
        },
    }


def verification_response_format() -> dict:
    """
    Returns the ``response_format`` dict for the ``web_research`` content
    verifier's ``{verified, confidence, reason}`` shape. Unlike the payload
    schema, this one has no optional fields, so it qualifies for OpenAI
    strict mode and ``strict`` is True.
    """
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "content_verification",
            "schema": {
                "type": "object",
                "properties": {
                    "verified": {"type": "boolean"},
                    "confidence": {"type": "integer", "minimum": 0, "maximum": 100},
                    "reason": {"type": "string"},
                },
                "required": ["verified", "confidence", "reason"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
