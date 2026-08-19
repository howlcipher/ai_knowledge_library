#!/usr/bin/env python3
"""
human_boundary.py

Human authority boundary enforcement and structured decision packet generation.
Guarantees that high-risk, destructive, financial, or security-sensitive actions
pause at AWAITING_HUMAN with complete evidence before proceeding.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from src.control_plane.hygiene_policy import (
    PolicyChangeType,
    PolicyEvaluationResult,
)
from src.control_plane.reconciliation import ReconciliationResult
from src.control_plane.task_spec import TaskSpec
from src.control_plane.verification import VerificationPlan

HUMAN_BOUNDARY_TRIGGERS = {
    "production_deployment": "Production deployment or live environment modification",
    "infrastructure_apply": "Infrastructure-as-code apply (e.g. terraform apply, k8s apply)",
    "destructive_database_change": "Destructive database migration (DROP TABLE/COLUMN, truncate)",
    "credential_provisioning": "Credential, token, or secret creation/rotation",
    "paid_service_usage": "Paid API or service consumption requiring user billing approval",
    "external_dependency_addition": "Adding new external dependencies or modifying license scope",
    "external_messaging": "Sending outbound emails, messages, webhooks, or notifications",
    "package_publishing": "Publishing packages or binaries to public registries or releases",
    "job_submission": "Submitting job applications, resumes, or external forms",
    "security_policy_exception": "Overriding or relaxing established security or anti-manipulation rules",
    "slop_debt_acceptance": (
        "Accepting new repository debt tombstone or repointing existing debt without prior policy authorization"
    ),
    "hygiene_policy_weakening": (
        "Weakening repository hygiene scan scope, ignore patterns, detector parameters, or provider settings"
    ),
    "hygiene_policy_violation": (
        "Prohibited repository hygiene policy violation (ceiling increase or configuration deletion)"
    ),
}


@dataclass
class HumanDecisionPacket:
    """Concise decision packet presented to a human operator for sign-off."""

    task_id: str
    objective: str
    change_summary: str
    boundary_triggers: List[str]
    evidence: List[str]
    risks: List[str]
    review_findings_summary: Dict[str, int]
    verification_status: str
    recommended_action: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def render_markdown(self) -> str:
        triggers_str = "\n".join(f"- ⚠️ **{t}**: {HUMAN_BOUNDARY_TRIGGERS.get(t, t)}" for t in self.boundary_triggers)
        evidence_str = "\n".join(f"- {e}" for e in self.evidence) or "None recorded."
        risks_str = "\n".join(f"- {r}" for r in self.risks) or "None recorded."
        findings_text = (
            f"{self.review_findings_summary.get('total', 0)} total ("
            f"{self.review_findings_summary.get('blocker', 0)} blockers, "
            f"{self.review_findings_summary.get('high', 0)} highs)"
        )

        return f"""# 🛑 Human Authority Decision Packet: Task `{self.task_id}`

## Objective
{self.objective}

## Boundary Triggers (Human Authorization Required)
{triggers_str}

## Proposed Change Summary
{self.change_summary}

## Verification Status
- **Automated Verification:** `{self.verification_status}`
- **Review Findings:** {findings_text}

## Key Evidence
{evidence_str}

## Identified Risks
{risks_str}

## Recommended Action
{self.recommended_action}

---
*Awaiting explicit human approval. Lack of response is treated as DENIED (fail-closed).*
"""


@dataclass
class BoundaryCheckResult:
    """Result of evaluating human authority boundaries."""

    requires_human_approval: bool
    triggered_boundaries: List[str] = field(default_factory=list)
    decision_packet: Optional[HumanDecisionPacket] = None


class HumanBoundaryGate:
    """Evaluates task intent, actions, and risk against human authority policies."""

    @classmethod
    def evaluate(
        cls,
        task: TaskSpec,
        planned_actions: List[str],
        change_summary: str = "",
        reconciliation: Optional[ReconciliationResult] = None,
        verification: Optional[VerificationPlan] = None,
        hygiene_policy: Optional[PolicyEvaluationResult] = None,
    ) -> BoundaryCheckResult:
        """
        Determines whether the task hits a human authority boundary.
        Distinguishes quality improvements (autonomously permitted) from debt acceptance / weakening.
        """
        triggers: List[str] = []

        # 1. Inspect task requirements
        if task.human_approval_requirements:
            for req in task.human_approval_requirements:
                if req in HUMAN_BOUNDARY_TRIGGERS and req not in triggers:
                    triggers.append(req)

        # 2. Inspect planned actions and commands
        actions_str = " ".join(planned_actions).lower()
        if "terraform apply" in actions_str or "kubectl apply" in actions_str:
            if "infrastructure_apply" not in triggers:
                triggers.append("infrastructure_apply")

        if "drop table" in actions_str or "drop column" in actions_str or "truncate" in actions_str:
            if "destructive_database_change" not in triggers:
                triggers.append("destructive_database_change")

        if "publish" in actions_str or "twine upload" in actions_str or "npm publish" in actions_str:
            if "package_publishing" not in triggers:
                triggers.append("package_publishing")

        if "sendmail" in actions_str or "smtp" in actions_str or "webhook" in actions_str:
            if "external_messaging" not in triggers:
                triggers.append("external_messaging")

        # 3. Evaluate semantic hygiene policy results
        if hygiene_policy:
            if hygiene_policy.is_hard_rejected:
                if "hygiene_policy_violation" not in triggers:
                    triggers.append("hygiene_policy_violation")
            if hygiene_policy.verdict == PolicyChangeType.DEBT_ACCEPTANCE:
                if "slop_debt_acceptance" not in triggers:
                    triggers.append("slop_debt_acceptance")
            elif hygiene_policy.verdict == PolicyChangeType.WEAKENING:
                if "hygiene_policy_weakening" not in triggers:
                    triggers.append("hygiene_policy_weakening")
            elif hygiene_policy.verdict == PolicyChangeType.UNKNOWN:
                if "security_policy_exception" not in triggers:
                    triggers.append("security_policy_exception")
        else:
            # Fallback heuristic when policy evaluation object is not pre-computed
            if (
                "tombstone add" in actions_str
                or "accept_debt" in actions_str
                or "write .slop/tombstones" in actions_str
                or ("tombstone" in actions_str and "delete" not in actions_str and "stale" not in actions_str)
            ):
                if "slop_debt_acceptance" not in triggers:
                    triggers.append("slop_debt_acceptance")

            if "ceiling increase" in actions_str:
                if "hygiene_policy_violation" not in triggers:
                    triggers.append("hygiene_policy_violation")

        # 4. Inspect reconciliation findings for unresolved blockers or security human reviews
        if reconciliation and reconciliation.requires_human_judgment:
            if "security_policy_exception" not in triggers:
                triggers.append("security_policy_exception")

        # 5. Critical risk tasks always trigger human authority
        if task.risk_level == "critical" and "production_deployment" not in triggers:
            triggers.append("production_deployment")

        if not triggers:
            return BoundaryCheckResult(requires_human_approval=False)

        # Build decision packet
        evidence_list: List[str] = []
        if verification:
            for step in verification.steps:
                evidence_list.append(f"Step '{step.name}': {step.status} (exit {step.exit_code})")

        if hygiene_policy and hygiene_policy.changes:
            for c in hygiene_policy.changes:
                evidence_list.append(f"Policy Change [{c.change_type.value.upper()}]: {c.description}")

        risks_list: List[str] = []
        for t in triggers:
            risks_list.append(f"Policy boundary '{t}': {HUMAN_BOUNDARY_TRIGGERS.get(t, t)}")

        findings_summary = {
            "total": len(reconciliation.findings) if reconciliation else 0,
            "blocker": reconciliation.unresolved_blockers if reconciliation else 0,
            "high": reconciliation.unresolved_highs if reconciliation else 0,
        }

        rec_action = "Review diff and evidence packet, then provide explicit approval or rejection."
        if "hygiene_policy_violation" in triggers:
            rec_action = "HARD REJECT: Prohibited ceiling inflation or policy violation must be remediated in code."

        summary_text = change_summary
        if not summary_text and hygiene_policy:
            summary_text = hygiene_policy.summary
        if not summary_text:
            summary_text = "Pending review & human confirmation."

        packet = HumanDecisionPacket(
            task_id=task.task_id,
            objective=task.objective,
            change_summary=summary_text,
            boundary_triggers=triggers,
            evidence=evidence_list,
            risks=risks_list,
            review_findings_summary=findings_summary,
            verification_status=verification.overall_status if verification else "unverified",
            recommended_action=rec_action,
        )

        return BoundaryCheckResult(
            requires_human_approval=True,
            triggered_boundaries=triggers,
            decision_packet=packet,
        )
