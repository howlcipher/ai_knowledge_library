#!/usr/bin/env python3
"""
task_spec.py

Canonical machine-readable representation of an engineering task and its lifecycle.
"""

from dataclasses import dataclass, field, asdict, fields
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import yaml

TASK_SPEC_SCHEMA_VERSION = "ai.task_spec/v1"

VALID_TASK_STATES = {
    "discovered",
    "planned",
    "implementing",
    "reviewing",
    "remediating",
    "verifying",
    "awaiting_human",
    "complete",
    "failed",
    "blocked",
}

VALID_RISK_LEVELS = {"low", "medium", "high", "critical"}
VALID_REASONING_TIERS = {"tier_1", "tier_2", "tier_3"}
VALID_TASK_CLASSES = {
    "bug_fix",
    "feature",
    "refactor",
    "security_patch",
    "test_improvement",
    "infrastructure",
    "docs",
    "automation",
    "other",
}

STATE_TRANSITIONS: Dict[str, Set[str]] = {
    "discovered": {"planned", "blocked", "failed"},
    "planned": {"implementing", "blocked", "failed"},
    "implementing": {"reviewing", "verifying", "blocked", "failed"},
    "reviewing": {"remediating", "verifying", "awaiting_human", "blocked", "failed"},
    "remediating": {"reviewing", "verifying", "blocked", "failed"},
    "verifying": {"awaiting_human", "complete", "remediating", "blocked", "failed"},
    "awaiting_human": {
        "complete",
        "implementing",
        "remediating",
        "verifying",
        "blocked",
        "failed",
    },
    "blocked": {
        "discovered",
        "planned",
        "implementing",
        "reviewing",
        "remediating",
        "verifying",
        "failed",
    },
    "failed": {"discovered", "planned"},
    "complete": {"discovered"},  # Can reopen if a regression is discovered
}


class InvalidStateTransitionError(ValueError):
    """Raised when an illegal task state transition is attempted."""
    pass


class TaskSpecValidationError(ValueError):
    """Raised when a task specification fails schema or semantic validation."""
    pass


@dataclass
class TaskSpec:
    """Represents a discrete engineering task handled by the multi-agent control plane."""

    task_id: str
    repository: str
    objective: str
    acceptance_criteria: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    task_class: str = "feature"
    risk_level: str = "medium"
    required_skills: List[str] = field(default_factory=list)
    recommended_reasoning_tier: str = "tier_2"
    preferred_agent: Optional[str] = None
    recommended_agent: Optional[str] = None
    actual_agent: Optional[str] = None
    is_override: Optional[bool] = None
    override_reason: Optional[str] = None
    allowed_tools: List[str] = field(default_factory=list)
    prohibited_actions: List[str] = field(default_factory=list)
    verification_requirements: List[str] = field(default_factory=list)
    reviewer_requirements: List[str] = field(default_factory=list)
    human_approval_requirements: List[str] = field(default_factory=list)
    current_state: str = "discovered"
    task_journal_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    schema: str = TASK_SPEC_SCHEMA_VERSION

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        """Validates internal fields against allowed enums and non-empty constraints."""
        if not self.task_id or not isinstance(self.task_id, str):
            raise TaskSpecValidationError("task_id must be a non-empty string")
        if not self.repository or not isinstance(self.repository, str):
            raise TaskSpecValidationError("repository must be a non-empty string")
        if not self.objective or not isinstance(self.objective, str):
            raise TaskSpecValidationError("objective must be a non-empty string")
        if self.task_class not in VALID_TASK_CLASSES:
            raise TaskSpecValidationError(
                f"task_class '{self.task_class}' invalid. Allowed: {sorted(VALID_TASK_CLASSES)}"
            )
        if self.risk_level not in VALID_RISK_LEVELS:
            raise TaskSpecValidationError(
                f"risk_level '{self.risk_level}' invalid. Allowed: {sorted(VALID_RISK_LEVELS)}"
            )
        if self.recommended_reasoning_tier not in VALID_REASONING_TIERS:
            raise TaskSpecValidationError(
                f"recommended_reasoning_tier '{self.recommended_reasoning_tier}' invalid."
            )
        if self.current_state not in VALID_TASK_STATES:
            raise TaskSpecValidationError(
                f"current_state '{self.current_state}' invalid. Allowed: {sorted(VALID_TASK_STATES)}"
            )
        if self.schema != TASK_SPEC_SCHEMA_VERSION:
            raise TaskSpecValidationError(
                f"schema '{self.schema}' invalid. Expected '{TASK_SPEC_SCHEMA_VERSION}'"
            )

    def transition_to(self, new_state: str, reason: str = "") -> None:
        """
        Transitions the task to a new lifecycle state.
        Raises InvalidStateTransitionError if the transition is illegal.
        """
        if new_state not in VALID_TASK_STATES:
            raise InvalidStateTransitionError(f"Unknown target state: {new_state}")

        allowed = STATE_TRANSITIONS.get(self.current_state, set())
        if new_state not in allowed:
            raise InvalidStateTransitionError(
                f"Cannot transition task '{self.task_id}' from '{self.current_state}' to '{new_state}'. "
                f"Allowed transitions from '{self.current_state}': {sorted(allowed)}"
            )

        self.current_state = new_state
        if "history" not in self.metadata:
            self.metadata["history"] = []
        self.metadata["history"].append(
            {"to_state": new_state, "reason": reason}
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts TaskSpec to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskSpec":
        """Constructs a TaskSpec from a dictionary."""
        d = dict(data)
        d.pop("schema", None)
        valid_fields = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in d.items() if k in valid_fields}
        return cls(schema=TASK_SPEC_SCHEMA_VERSION, **filtered)

    def to_json(self, indent: int = 2) -> str:
        """Serializes TaskSpec to formatted JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> "TaskSpec":
        """Deserializes TaskSpec from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def to_yaml(self) -> str:
        """Serializes TaskSpec to YAML string."""
        return yaml.dump(self.to_dict(), sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "TaskSpec":
        """Deserializes TaskSpec from YAML string."""
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)

    def save_to_file(self, file_path: str) -> None:
        """Saves the specification to a file based on file extension (.json, .yaml, .yml)."""
        p = Path(file_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.suffix in (".yaml", ".yml"):
            p.write_text(self.to_yaml(), encoding="utf-8")
        else:
            p.write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def load_from_file(cls, file_path: str) -> "TaskSpec":
        """Loads a specification from a .json or .yaml file."""
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"Task specification file not found: {file_path}")
        text = p.read_text(encoding="utf-8")
        if p.suffix in (".yaml", ".yml"):
            return cls.from_yaml(text)
        return cls.from_json(text)
