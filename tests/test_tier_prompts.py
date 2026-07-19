import re

from src.core.tier_prompts import TIER1_PROMPT, TIER2_PROMPT, TIER3_PROMPT

SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")


def _placeholder_in(prompt: str) -> str:
    match = re.search(r'content\.sha256 to a placeholder of 64 zero characters \("([^"]+)"\)', prompt)
    assert match, "expected a quoted 64-zero placeholder instruction"
    return match.group(1)


def test_tier3_prompt_placeholder_matches_schema_hash_pattern():
    assert SHA256_PATTERN.match(_placeholder_in(TIER3_PROMPT))


def test_tier1_prompt_placeholder_matches_schema_hash_pattern():
    assert SHA256_PATTERN.match(_placeholder_in(TIER1_PROMPT))


def test_tier3_prompt_does_not_ask_agent_to_compute_hash():
    assert "SHA-256 of the UTF-8 bytes" not in TIER3_PROMPT


def test_tier1_prompt_does_not_ask_agent_to_compute_hash():
    assert "Recompute content.sha256" not in TIER1_PROMPT


def test_tier2_prompt_still_forbids_content_mutation():
    assert "You must not modify content.body or content.sha256" in TIER2_PROMPT
