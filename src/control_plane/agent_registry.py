#!/usr/bin/env python3
"""
agent_registry.py

Declarative registry describing available agent types and capabilities.
"""

from dataclasses import dataclass, field, asdict
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

AGENT_REGISTRY_SCHEMA_VERSION = "ai.agent_registry/v1"


@dataclass
class AgentProfile:
    """Represents a declarative profile for an AI agent type based on observable capabilities."""

    agent_id: str
    name: str
    provider: str
    interface: str  # "cli", "headless_cli", "api", "ide"
    capabilities: List[str] = field(default_factory=list)
    available_tools: List[str] = field(default_factory=list)
    reasoning_tier: str = "tier_2"  # "tier_1", "tier_2", "tier_3"
    supports_repository_access: bool = True
    supports_command_execution: bool = True
    supports_long_running_tasks: bool = False
    supports_independent_sessions: bool = True
    cost_class: str = "subscription_included"  # "free_local", "subscription_included", "paid_api"
    availability: str = "available"  # "available", "degraded", "unavailable"
    operator_preference: Optional[str] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentProfile":
        return cls(**data)


BUILTIN_AGENTS: List[AgentProfile] = [
    AgentProfile(
        agent_id="claude_code",
        name="Claude Code",
        provider="anthropic",
        interface="cli",
        capabilities=[
            "code_generation",
            "file_editing",
            "code_review",
            "terminal_execution",
            "git_operations",
            "architectural_reasoning",
            "deep_debugging",
            "autonomous_workflow",
        ],
        available_tools=["bash", "glob", "grep", "read", "edit", "mcp"],
        reasoning_tier="tier_1",
        supports_repository_access=True,
        supports_command_execution=True,
        supports_long_running_tasks=True,
        supports_independent_sessions=True,
        cost_class="subscription_included",
        availability="available",
        operator_preference="Default primary interactive orchestrator and architectural agent.",
        notes="Best suited for complex architecture, task orchestration, and difficult refactoring.",
    ),
    AgentProfile(
        agent_id="codex",
        name="Codex CLI",
        provider="openai",
        interface="cli",
        capabilities=[
            "code_generation",
            "file_editing",
            "code_review",
            "terminal_execution",
            "git_operations",
        ],
        available_tools=["bash", "file_search", "patch"],
        reasoning_tier="tier_2",
        supports_repository_access=True,
        supports_command_execution=True,
        supports_long_running_tasks=False,
        supports_independent_sessions=True,
        cost_class="subscription_included",
        availability="available",
        operator_preference=None,
        notes="Effective for standard implementation, boilerplate, and routine features.",
    ),
    AgentProfile(
        agent_id="gemini_cli",
        name="Gemini CLI",
        provider="google",
        interface="cli",
        capabilities=[
            "code_generation",
            "file_editing",
            "code_review",
            "terminal_execution",
            "git_operations",
            "architectural_reasoning",
        ],
        available_tools=["bash", "file_ops", "search"],
        reasoning_tier="tier_2",
        supports_repository_access=True,
        supports_command_execution=True,
        supports_long_running_tasks=False,
        supports_independent_sessions=True,
        cost_class="subscription_included",
        availability="available",
        operator_preference="High-context analytical tasks and multi-file code exploration.",
        notes="Large context window and strong analytical reasoning.",
    ),
    AgentProfile(
        agent_id="devin_cli",
        name="Devin CLI",
        provider="cognition",
        interface="cli",
        capabilities=[
            "code_generation",
            "file_editing",
            "code_review",
            "terminal_execution",
            "git_operations",
            "autonomous_workflow",
            "deep_debugging",
        ],
        available_tools=["browser", "terminal", "editor", "planner"],
        reasoning_tier="tier_1",
        supports_repository_access=True,
        supports_command_execution=True,
        supports_long_running_tasks=True,
        supports_independent_sessions=True,
        cost_class="subscription_included",
        availability="available",
        operator_preference="Multi-step autonomous execution and full environment setups.",
        notes="Autonomous multi-step investigation, environment setup, and verification.",
    ),
    AgentProfile(
        agent_id="agy",
        name="Antigravity CLI (agy)",
        provider="google",
        interface="headless_cli",
        capabilities=[
            "code_generation",
            "file_editing",
            "code_review",
            "git_operations",
        ],
        available_tools=["file_edit", "diff_apply"],
        reasoning_tier="tier_2",
        supports_repository_access=True,
        supports_command_execution=False,
        supports_long_running_tasks=False,
        supports_independent_sessions=False,
        cost_class="subscription_included",
        availability="available",
        operator_preference="Headless code implementation delegate.",
        notes="Headless delegate; requires explicit absolute paths and diff inspection.",
    ),
    AgentProfile(
        agent_id="local_ollama",
        name="Local Ollama",
        provider="local",
        interface="api",
        capabilities=[
            "code_generation",
            "file_editing",
            "code_review",
        ],
        available_tools=["api_generate"],
        reasoning_tier="tier_3",
        supports_repository_access=False,
        supports_command_execution=False,
        supports_long_running_tasks=False,
        supports_independent_sessions=True,
        cost_class="free_local",
        availability="available",
        operator_preference="Zero egress private helper subtasks.",
        notes="Zero external egress; ideal for private, small, well-bounded helper subtasks.",
    ),
]


class AgentRegistry:
    """Manages agent type definitions and capabilities."""

    def __init__(self, agents: Optional[List[AgentProfile]] = None):
        self._agents: Dict[str, AgentProfile] = {}
        initial = agents if agents is not None else BUILTIN_AGENTS
        for profile in initial:
            self.register_agent(profile)

    def register_agent(self, profile: AgentProfile) -> None:
        """Registers or updates an agent profile."""
        self._agents[profile.agent_id] = profile

    def get_agent(self, agent_id: str) -> Optional[AgentProfile]:
        """Retrieves an agent profile by agent_id."""
        return self._agents.get(agent_id)

    def list_agents(self, only_available: bool = False) -> List[AgentProfile]:
        """Lists all registered agent profiles."""
        agents = list(self._agents.values())
        if only_available:
            agents = [a for a in agents if a.availability == "available"]
        return agents

    def filter_agents(
        self,
        capability: Optional[str] = None,
        reasoning_tier: Optional[str] = None,
        cost_class: Optional[str] = None,
        interface: Optional[str] = None,
        only_available: bool = True,
    ) -> List[AgentProfile]:
        """Filters agents matching multiple criteria."""
        results = self.list_agents(only_available=only_available)
        if capability:
            results = [a for a in results if capability in a.capabilities]
        if reasoning_tier:
            results = [a for a in results if a.reasoning_tier == reasoning_tier]
        if cost_class:
            results = [a for a in results if a.cost_class == cost_class]
        if interface:
            results = [a for a in results if a.interface == interface]
        return results

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema": AGENT_REGISTRY_SCHEMA_VERSION,
            "agents": [a.to_dict() for a in self._agents.values()],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentRegistry":
        agents_data = data.get("agents", [])
        profiles = [AgentProfile.from_dict(item) for item in agents_data]
        return cls(agents=profiles)

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "AgentRegistry":
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)

    def save_to_file(self, file_path: str) -> None:
        p = Path(file_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.suffix in (".yaml", ".yml"):
            p.write_text(self.to_yaml(), encoding="utf-8")
        else:
            p.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load_from_file(cls, file_path: str) -> "AgentRegistry":
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"Registry file not found: {file_path}")
        text = p.read_text(encoding="utf-8")
        if p.suffix in (".yaml", ".yml"):
            return cls.from_yaml(text)
        return cls.from_dict(json.loads(text))
