"""
Multi-Agent Engineering Control Plane.

Provides task specification, agent capability registry, deterministic routing,
specialized independent reviewers, review reconciliation, verification plans,
evidence ledgers, transparent performance metrics, project adapters, and human authority boundaries.
"""

from src.control_plane.task_spec import (
    TaskSpec,
    InvalidStateTransitionError,
    TaskSpecValidationError,
    VALID_TASK_STATES,
)
from src.control_plane.agent_registry import (
    AgentProfile,
    AgentRegistry,
    BUILTIN_AGENTS,
)
from src.control_plane.router import (
    TaskRouter,
    RoutingDecision,
)
from src.control_plane.reviewers import (
    ReviewerRole,
    REVIEWER_ROLES,
    get_reviewer_role,
    list_reviewer_roles,
)
from src.control_plane.reconciliation import (
    ReviewFinding,
    ReconciliationResult,
    ReviewReconciler,
    ReconciliationValidationError,
)
from src.control_plane.verification import (
    VerificationStep,
    VerificationPlan,
    VerificationError,
)
from src.control_plane.evidence_ledger import (
    EvidenceEntry,
    EvidenceLedger,
    redact_sensitive_data,
)
from src.control_plane.metrics import (
    AgentMetricSummary,
    PerformanceMetricsSummary,
    MetricsCalculator,
)
from src.control_plane.project_adapter import (
    ProjectContext,
    ProjectAdapter,
)
from src.control_plane.human_boundary import (
    HumanBoundaryGate,
    HumanDecisionPacket,
    BoundaryCheckResult,
    HUMAN_BOUNDARY_TRIGGERS,
)

__all__ = [
    "TaskSpec",
    "InvalidStateTransitionError",
    "TaskSpecValidationError",
    "VALID_TASK_STATES",
    "AgentProfile",
    "AgentRegistry",
    "BUILTIN_AGENTS",
    "TaskRouter",
    "RoutingDecision",
    "ReviewerRole",
    "REVIEWER_ROLES",
    "get_reviewer_role",
    "list_reviewer_roles",
    "ReviewFinding",
    "ReconciliationResult",
    "ReviewReconciler",
    "ReconciliationValidationError",
    "VerificationStep",
    "VerificationPlan",
    "VerificationError",
    "EvidenceEntry",
    "EvidenceLedger",
    "redact_sensitive_data",
    "AgentMetricSummary",
    "PerformanceMetricsSummary",
    "MetricsCalculator",
    "ProjectContext",
    "ProjectAdapter",
    "HumanBoundaryGate",
    "HumanDecisionPacket",
    "BoundaryCheckResult",
    "HUMAN_BOUNDARY_TRIGGERS",
]
