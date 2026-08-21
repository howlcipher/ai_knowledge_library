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

    def _normalize(self, agent_id: str) -> str:
        return AgentBackendRegistry.normalize_agent_id(agent_id)

    def get_status(self, agent_id: str) -> ProviderAvailabilityStatus:
        nid = self._normalize(agent_id)
        if nid in self._provider_states:
            return self._provider_states[nid].status
        return ProviderAvailabilityStatus.UNKNOWN

    def set_status(self, agent_id: str, status: ProviderAvailabilityStatus, event: Optional[ProviderExhaustionEvent] = None) -> None:
        nid = self._normalize(agent_id)
        if nid not in self._provider_states:
            self._provider_states[nid] = ProviderStatus(agent_id=nid, name=nid)
        self._provider_states[nid].status = status
        self._provider_states[nid].last_checked = datetime.now(timezone.utc).isoformat()
        if event:
            self._provider_states[nid].exhaustion_event = event

    def reset_transient_exhaustion(self) -> None:
        """Resets transient rate-limited and session-exhausted states on new or resumed campaigns."""
        for agent_id, status_obj in self._provider_states.items():
            backend = AgentBackendRegistry.get_backend(agent_id)
            if backend.is_available():
                status_obj.status = ProviderAvailabilityStatus.AVAILABLE
                status_obj.exhaustion_event = None
            else:
                status_obj.status = ProviderAvailabilityStatus.UNAVAILABLE

    def get_all_statuses(self) -> Dict[str, str]:
        """Returns snapshot of current provider statuses."""
        return {aid: s.status.value for aid, s in self._provider_states.items()}

    def has_available_providers(self) -> bool:
        """Returns True if at least one provider is currently AVAILABLE."""
        return any(
            s.status == ProviderAvailabilityStatus.AVAILABLE
            for s in self._provider_states.values()
        )

    def detect_exhaustion(self, agent_id: str, result: AgentExecutionResult, task_id: Optional[str] = None) -> Optional[ProviderExhaustionEvent]:
        """
        Distinguishes provider availability failures from normal engineering failures.
        """
        nid = self._normalize(agent_id)
        if result.success:
            if nid in self._provider_states:
                self._provider_states[nid].status = ProviderAvailabilityStatus.AVAILABLE
                self._provider_states[nid].success_count += 1
                self._provider_states[nid].total_duration_seconds += result.duration_seconds
            return None

        combined_output = (result.stderr + "\n" + result.stdout).lower()

        # Check binary missing
        if result.exit_code == 127 or "not installed" in combined_output or "not found" in combined_output:
            event = ProviderExhaustionEvent(
                agent_id=nid,
                failure_type="unavailable",
                raw_error=result.stderr.strip() or "Binary not found",
                task_id=task_id,
            )
            self.set_status(nid, ProviderAvailabilityStatus.UNAVAILABLE, event)
            return event

        # Check provider exhaustion signatures across specific provider patterns and generic patterns
        patterns = list(EXHAUSTION_PATTERNS.get(nid, []))
        generic_exhaustion = [
            "quota exceeded",
            "rate limit",
            "rate_limit",
            "usage limit",
            "session limit",
            "credits exhausted",
            "insufficient quota",
            "429 too many requests",
            "resource exhausted",
            "out of capacity",
            "session exhausted",
        ]
        all_patterns = patterns + generic_exhaustion

        for pattern in all_patterns:
            if pattern in combined_output:
                ftype = "rate_limit" if "rate" in pattern or "429" in pattern else "session_limit"
                event = ProviderExhaustionEvent(
                    agent_id=nid,
                    failure_type=ftype,
                    raw_error=result.stderr.strip() or pattern,
                    task_id=task_id,
                )
                new_status = ProviderAvailabilityStatus.RATE_LIMITED if ftype == "rate_limit" else ProviderAvailabilityStatus.SESSION_EXHAUSTED
                self.set_status(nid, new_status, event)
                return event

        # Normal engineering failure: tests failed, compiler syntax error, etc.
        # Do NOT mark provider as exhausted!
        return None

    def is_all_exhausted(self) -> bool:
        """Returns True if all configured providers are in an exhausted or rate-limited status."""
        statuses = [ps.status for ps in self._provider_states.values()]
        return bool(statuses) and all(
            st in (ProviderAvailabilityStatus.SESSION_EXHAUSTED, ProviderAvailabilityStatus.RATE_LIMITED)
            for st in statuses
        )

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
        avoid_norm = self._normalize(avoid_provider) if avoid_provider else (
            self._normalize(self.avoid_provider) if self.avoid_provider else None
        )
        pref_agent_norm = self._normalize(preferred_agent) if preferred_agent else None
        pref_list = [self._normalize(a) for a in TASK_SUITABILITY_PREFERENCES.get(task_category, TASK_SUITABILITY_PREFERENCES["code_heavy"])]

        candidates: List[str] = []

        # If user specified preferred agent and it's available, place first
        if pref_agent_norm and self.get_status(pref_agent_norm) == ProviderAvailabilityStatus.AVAILABLE:
            candidates.append(pref_agent_norm)

        for agent_id in pref_list:
            if agent_id not in candidates and self.get_status(agent_id) == ProviderAvailabilityStatus.AVAILABLE:
                candidates.append(agent_id)

        # Append degraded/unknown agents before avoided providers
        for agent_id in pref_list:
            if agent_id not in candidates and self.get_status(agent_id) == ProviderAvailabilityStatus.UNKNOWN:
                candidates.append(agent_id)

        # Move avoid_provider to the very end
        if avoid_norm and avoid_norm in candidates:
            candidates.remove(avoid_norm)
            candidates.append(avoid_norm)

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
        impl_norm = self._normalize(implementing_agent_id)
        available_agents = [
            self._normalize(a.agent_id)
            for a in self.registry.list_agents()
            if self.get_status(a.agent_id) == ProviderAvailabilityStatus.AVAILABLE
        ]

        distinct_candidates = [a for a in available_agents if a != impl_norm]
        role_mapping: Dict[str, str] = {}
        diversity_achieved = True

        for idx, role in enumerate(required_roles):
            if distinct_candidates:
                chosen = distinct_candidates[idx % len(distinct_candidates)]
                role_mapping[role] = chosen
            elif allow_same_provider and available_agents:
                role_mapping[role] = impl_norm
                diversity_achieved = False
            else:
                role_mapping[role] = impl_norm
                diversity_achieved = False

        return role_mapping, diversity_achieved
