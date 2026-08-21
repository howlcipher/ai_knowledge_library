#!/usr/bin/env python3
"""
provider_pool.py

Manages multi-agent provider pool availability, task suitability ranking,
quota exhaustion detection, dynamic provider fallback, and cross-provider review.
Distinguishes transient provider exhaustion from engineering failures.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import re
import shutil
import time
from typing import Any, Dict, List, Optional, Set, Tuple

from src.control_plane.agent_execution import (
    AgentBackend,
    AgentBackendRegistry,
    AgentExecutionResult,
)
from src.control_plane.agent_registry import AgentProfile, AgentRegistry
from src.control_plane.task_spec import DataClassSerializationMixin

PROVIDER_POOL_SCHEMA_VERSION = "howlplane.provider_pool/v1"


class ProviderAvailabilityStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RATE_LIMITED = "RATE_LIMITED"
    SESSION_EXHAUSTED = "SESSION_EXHAUSTED"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"


# Task suitability preference order
TASK_SUITABILITY_PREFERENCES: Dict[str, List[str]] = {
    "routine": ["agy", "codex", "devin_cli", "claude_code", "local_ollama"],
    "code_heavy": ["codex", "agy", "devin_cli", "claude_code", "local_ollama"],
    "large_autonomous": ["devin_cli", "codex", "agy", "claude_code"],
    "architecture_security": ["claude_code", "codex", "agy", "devin_cli"],
}

# Known provider exhaustion and rate limit signatures
EXHAUSTION_PATTERNS: Dict[str, List[str]] = {
    "claude_code": [
        "usage limit reached",
        "rate limit exceeded",
        "quota exceeded",
        "credit limit",
        "429 too many requests",
        "overloaded_error",
        "insufficient_quota",
    ],
    "codex": [
        "session limit reached",
        "rate_limit_exceeded",
        "insufficient_quota",
        "quota exceeded",
        "out of capacity",
        "usage limit",
    ],
    "agy": [
        "quota exhausted",
        "rate limit",
        "resource exhausted",
        "resource_exhausted",
        "token limit",
        "exceeded your current quota",
    ],
    "devin_cli": [
        "session limit",
        "quota unavailable",
        "rate limited",
        "credits exhausted",
        "insufficient funds",
    ],
    "local_ollama": [
        "connection refused",
        "not running",
        "server unavailable",
    ],
}


@dataclass
class ProviderExhaustionEvent(DataClassSerializationMixin):
    """Event recording when a provider encounters quota exhaustion or availability failure."""

    agent_id: str
    failure_type: str  # "session_limit", "rate_limit", "quota_exhausted", "unavailable"
    raw_error: str
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    task_id: Optional[str] = None


@dataclass
class ProviderStatus(DataClassSerializationMixin):
    """Live state of an agent provider in the session."""

    agent_id: str
    name: str
    status: ProviderAvailabilityStatus = ProviderAvailabilityStatus.AVAILABLE
    last_checked: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    consecutive_failures: int = 0
    exhaustion_event: Optional[ProviderExhaustionEvent] = None
    success_count: int = 0
    total_duration_seconds: float = 0.0


class ProviderPoolManager:
    """
    Manages provider selection, exhaustion detection, fallback routing,
    and cross-provider reviewer assignment.
    """

    def __init__(
        self,
        registry: Optional[AgentRegistry] = None,
        avoid_provider: Optional[str] = None,
        fallback_provider: Optional[str] = None,
    ):
        self.registry = registry or AgentRegistry()
        self.avoid_provider = avoid_provider
        self.fallback_provider = fallback_provider
        self._provider_states: Dict[str, ProviderStatus] = {}
        self._initialize_states()

    def _initialize_states(self) -> None:
        for p in self.registry.list_agents():
            # Check binary presence on PATH
            backend = AgentBackendRegistry.get_backend(p.agent_id)
            initial_status = ProviderAvailabilityStatus.AVAILABLE if backend.is_available() else ProviderAvailabilityStatus.UNAVAILABLE
            self._provider_states[p.agent_id] = ProviderStatus(
                agent_id=p.agent_id,
                name=p.name,
                status=initial_status,
            )

    def get_status(self, agent_id: str) -> ProviderAvailabilityStatus:
        if agent_id in self._provider_states:
            return self._provider_states[agent_id].status
        return ProviderAvailabilityStatus.UNKNOWN

    def set_status(self, agent_id: str, status: ProviderAvailabilityStatus, event: Optional[ProviderExhaustionEvent] = None) -> None:
        if agent_id not in self._provider_states:
            self._provider_states[agent_id] = ProviderStatus(agent_id=agent_id, name=agent_id)
        self._provider_states[agent_id].status = status
        self._provider_states[agent_id].last_checked = datetime.now(timezone.utc).isoformat()
        if event:
            self._provider_states[agent_id].exhaustion_event = event

    def detect_exhaustion(self, agent_id: str, result: AgentExecutionResult, task_id: Optional[str] = None) -> Optional[ProviderExhaustionEvent]:
        """
        Distinguishes provider availability failures from normal engineering failures.
        """
        if result.success:
            if agent_id in self._provider_states:
                self._provider_states[agent_id].status = ProviderAvailabilityStatus.AVAILABLE
                self._provider_states[agent_id].success_count += 1
                self._provider_states[agent_id].total_duration_seconds += result.duration_seconds
            return None

        combined_output = (result.stderr + "\n" + result.stdout).lower()

        # Check binary missing
        if result.exit_code == 127 or "not installed" in combined_output or "not found" in combined_output:
            event = ProviderExhaustionEvent(
                agent_id=agent_id,
                failure_type="unavailable",
                raw_error=result.stderr.strip() or "Binary not found",
                task_id=task_id,
            )
            self.set_status(agent_id, ProviderAvailabilityStatus.UNAVAILABLE, event)
            return event

        # Check provider exhaustion signatures
        patterns = EXHAUSTION_PATTERNS.get(agent_id, [])
        for pattern in patterns:
            if pattern in combined_output:
                ftype = "rate_limit" if "rate" in pattern else "session_limit"
                event = ProviderExhaustionEvent(
                    agent_id=agent_id,
                    failure_type=ftype,
                    raw_error=result.stderr.strip() or pattern,
                    task_id=task_id,
                )
                new_status = ProviderAvailabilityStatus.RATE_LIMITED if ftype == "rate_limit" else ProviderAvailabilityStatus.SESSION_EXHAUSTED
                self.set_status(agent_id, new_status, event)
                return event

        # Normal engineering failure: tests failed, compiler syntax error, etc.
        # Do NOT mark provider as exhausted!
        return None

    def select_candidates(
        self,
        task_category: str = "code_heavy",
        avoid_provider: Optional[str] = None,
        preferred_agent: Optional[str] = None,
    ) -> List[str]:
        """
        Ranks candidate agents by task suitability and availability,
        placing avoided/fallback providers last.
        """
        avoid = avoid_provider or self.avoid_provider or self.fallback_provider
        pref_list = TASK_SUITABILITY_PREFERENCES.get(task_category, TASK_SUITABILITY_PREFERENCES["code_heavy"])

        candidates: List[str] = []

        # If user specified preferred agent and it's available, place first
        if preferred_agent and self.get_status(preferred_agent) == ProviderAvailabilityStatus.AVAILABLE:
            candidates.append(preferred_agent)

        for agent_id in pref_list:
            if agent_id not in candidates and self.get_status(agent_id) == ProviderAvailabilityStatus.AVAILABLE:
                candidates.append(agent_id)

        # Append degraded/unknown agents before avoided providers
        for agent_id in pref_list:
            if agent_id not in candidates and self.get_status(agent_id) == ProviderAvailabilityStatus.UNKNOWN:
                candidates.append(agent_id)

        # Move avoid_provider to the very end
        if avoid and avoid in candidates:
            candidates.remove(avoid)
            candidates.append(avoid)

        return candidates

    def select_reviewers(
        self,
        implementing_agent_id: str,
        required_roles: List[str],
        allow_same_provider: bool = False,
    ) -> Tuple[Dict[str, str], bool]:
        """
        Selects independent reviewers from distinct providers whenever available.
        Returns mapping of role_id -> agent_id, and boolean indicating if full provider diversity was achieved.
        """
        available_agents = [
            a.agent_id
            for a in self.registry.list_agents()
            if self.get_status(a.agent_id) == ProviderAvailabilityStatus.AVAILABLE
        ]

        distinct_candidates = [a for a in available_agents if a != implementing_agent_id]
        role_mapping: Dict[str, str] = {}
        diversity_achieved = True

        for idx, role in enumerate(required_roles):
            if distinct_candidates:
                chosen = distinct_candidates[idx % len(distinct_candidates)]
                role_mapping[role] = chosen
            elif allow_same_provider and available_agents:
                role_mapping[role] = implementing_agent_id
                diversity_achieved = False
            else:
                role_mapping[role] = implementing_agent_id
                diversity_achieved = False

        return role_mapping, diversity_achieved
