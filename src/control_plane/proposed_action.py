#!/usr/bin/env python3
"""
proposed_action.py

Defines the structured representation of executable and consequential actions
distinguishing proposal/implementation artifacts from real-world side effects.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from src.control_plane.task_spec import DataClassSerializationMixin

PROPOSED_ACTION_SCHEMA_VERSION = "howlplane.proposed_action/v1"

CONSEQUENTIAL_RULES: List[Tuple[Tuple[str, ...], str, str, str, Optional[str]]] = [
    (
        ("create_release_candidate", "create release candidate", "release candidate tag", "tag release candidate", "howlchangeops"),
        "create_release_candidate",
        "high",
        "package_publishing",
        "howlchangeops",
    ),
    (
        ("terraform apply", "kubectl apply"),
        "infrastructure_apply",
        "critical",
        "infrastructure_apply",
        None,
    ),
    (
        ("drop table", "drop column", "truncate"),
        "destructive_database_change",
        "critical",
        "destructive_database_change",
        None,
    ),
    (
        ("twine upload", "npm publish", "publish package", "publish"),
        "package_publishing",
        "high",
        "package_publishing",
        None,
    ),
    (
        ("sendmail", "smtp", "webhook"),
        "external_messaging",
        "medium",
        "external_messaging",
        None,
    ),
    (
        ("production deploy", "deploy to prod", "deploy production"),
        "production_deployment",
        "critical",
        "production_deployment",
        None,
    ),
]


@dataclass
class ProposedAction(DataClassSerializationMixin):
    """Smallest useful representation of an executable/consequential action."""

    action_type: str
    target_repo: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    risk_level: str = "medium"
    requires_bounded_execution: bool = True
    authority_boundary: Optional[str] = None
    evidence_references: Dict[str, Any] = field(default_factory=dict)
    executor_id: Optional[str] = None
    decision_id: Optional[str] = None
    schema: str = PROPOSED_ACTION_SCHEMA_VERSION


def infer_proposed_actions(
    objective: str,
    repo_name: str,
    planned_actions: Optional[List[str]] = None,
    human_approval_requirements: Optional[List[str]] = None,
) -> List[ProposedAction]:
    """
    Infers explicit consequential actions from task metadata and planned actions.
    Distinguishes implementation proposals from executable side effects.
    """
    actions: List[ProposedAction] = []
    seen: set = set()
    combined = f"{objective} {' '.join(planned_actions or [])}".lower()

    for keywords, act_type, risk, boundary, executor in CONSEQUENTIAL_RULES:
        if any(kw in combined for kw in keywords) and act_type not in seen:
            seen.add(act_type)
            actions.append(
                ProposedAction(
                    action_type=act_type,
                    target_repo=repo_name,
                    risk_level=risk,
                    requires_bounded_execution=True,
                    authority_boundary=boundary,
                    executor_id=executor,
                )
            )

    if human_approval_requirements:
        for req in human_approval_requirements:
            if req not in seen:
                seen.add(req)
                exec_id = "howlchangeops" if req == "create_release_candidate" else None
                actions.append(
                    ProposedAction(
                        action_type=req,
                        target_repo=repo_name,
                        risk_level="critical" if "apply" in req or "destructive" in req else "high",
                        requires_bounded_execution=True,
                        authority_boundary=req,
                        executor_id=exec_id,
                    )
                )

    return actions
