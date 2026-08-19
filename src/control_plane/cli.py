#!/usr/bin/env python3
"""
cli.py

Deterministic command-line interface for the multi-agent engineering control plane.
"""

import argparse
from pathlib import Path
import sys
from typing import List, Optional

from src.control_plane.agent_registry import AgentRegistry
from src.control_plane.evidence_ledger import EvidenceEntry, EvidenceLedger
from src.control_plane.human_boundary import HumanBoundaryGate
from src.control_plane.metrics import MetricsCalculator
from src.control_plane.project_adapter import ProjectAdapter
from src.control_plane.reconciliation import ReviewFinding, ReviewReconciler
from src.control_plane.reviewers import list_reviewer_roles, get_reviewer_role
from src.control_plane.router import TaskRouter
from src.control_plane.task_spec import TaskSpec
from src.control_plane.verification import VerificationPlan


def cmd_init_task(args: argparse.Namespace) -> int:
    """Creates a new TaskSpec file."""
    spec = TaskSpec(
        task_id=args.task_id,
        repository=args.repo,
        objective=args.objective,
        acceptance_criteria=args.criteria or [],
        constraints=args.constraints or [],
        task_class=args.task_class or "feature",
        risk_level=args.risk,
        required_skills=args.skills or [],
        recommended_reasoning_tier=args.tier,
        preferred_agent=args.preferred_agent,
    )
    out_path = args.output or f"task_{spec.task_id}.yaml"
    spec.save_to_file(out_path)
    print(f"Task specification written to: {out_path}")
    return 0


def cmd_route_task(args: argparse.Namespace) -> int:
    """Routes a task specification to an agent and reviewers."""
    spec = TaskSpec.load_from_file(args.task_file)
    router = TaskRouter()
    decision = router.route(spec)

    print("=" * 60)
    print(f"TASK ROUTING DECISION: {spec.task_id}")
    print("=" * 60)
    print(f"Selected Agent: {decision.selected_agent_name} (`{decision.selected_agent_id}`)")
    print(f"Reasoning Tier: {decision.reasoning_tier}")
    print(f"Is Override:    {decision.is_override}")
    print(f"Rationale:      {decision.rationale}")
    print(f"Reviewers:      {', '.join(decision.recommended_reviewers)}")
    if decision.alternatives:
        print(f"Alternatives:   {', '.join(decision.alternatives)}")
    print("=" * 60)
    return 0


def cmd_briefs(args: argparse.Namespace) -> int:
    """Generates independent review briefs for a task diff."""
    spec = TaskSpec.load_from_file(args.task_file)
    diff_text = Path(args.diff_file).read_text(encoding="utf-8") if args.diff_file else ""

    router = TaskRouter()
    decision = router.route(spec)
    reviewers_to_run = args.roles or decision.recommended_reviewers

    out_dir = Path(args.output_dir or "review_briefs")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating review briefs for {len(reviewers_to_run)} roles in {out_dir}/...")
    for role_id in reviewers_to_run:
        role = get_reviewer_role(role_id)
        if not role:
            print(f"Warning: Unknown reviewer role '{role_id}', skipping.")
            continue
        brief = role.render_brief(task=spec, diff_content=diff_text)
        brief_file = out_dir / f"brief_{role_id}.md"
        brief_file.write_text(brief, encoding="utf-8")
        print(f" - Wrote: {brief_file}")
    return 0


def cmd_prepare_run(args: argparse.Namespace) -> int:
    """Prepares structured task run directory and reviewer briefs for cross-agent handoffs."""
    spec = TaskSpec.load_from_file(args.task_file)
    diff_text = Path(args.diff_file).read_text(encoding="utf-8") if args.diff_file else ""

    run_dir = Path(args.run_dir or f".task_runs/{spec.task_id}")
    reviews_dir = run_dir / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)

    # Save copy of task spec and diff
    spec.save_to_file(str(run_dir / "task.yaml"))
    if diff_text:
        (run_dir / "diff.patch").write_text(diff_text, encoding="utf-8")

    router = TaskRouter()
    decision = router.route(spec)
    reviewers_to_run = args.roles or decision.recommended_reviewers

    print(f"Preparing dogfood task run in {run_dir}/...")
    print(f"- Implementation Agent: {decision.selected_agent_name} (`{decision.selected_agent_id}`)")
    print(f"- Generating {len(reviewers_to_run)} independent reviewer briefs in {reviews_dir}/:")

    for role_id in reviewers_to_run:
        role = get_reviewer_role(role_id)
        if not role:
            continue
        brief = role.render_brief(task=spec, diff_content=diff_text)
        brief_file = reviews_dir / f"{role_id}.md"
        brief_file.write_text(brief, encoding="utf-8")
        print(f"   ✓ {brief_file.name}")

    # Write findings template
    template_file = run_dir / "findings_template.yaml"
    template_content = """# Review Findings Template
# Collect structured findings from independent reviewer roles below.
findings:
  # Example:
  # - id: "F001"
  #   reviewer_role: "test-falsifier"
  #   title: "Missing negative test case for edge input"
  #   severity: "high"
  #   category: "test_gap"
  #   location: "tests/test_feature.py:45"
  #   description: "Test does not check None input handling."
  #   evidence: "Calling feature(None) raises unhandled exception."
  #   suggested_fix: "Add test_feature_handles_none_gracefully."
"""
    template_file.write_text(template_content, encoding="utf-8")
    print(f"- Template written: {template_file}")
    print(f"\nTask run initialized successfully at {run_dir}.")
    return 0


def cmd_reconcile(args: argparse.Namespace) -> int:
    """Reconciles findings from a YAML/JSON findings file."""
    import yaml
    findings_raw = yaml.safe_load(Path(args.findings_file).read_text(encoding="utf-8"))
    if isinstance(findings_raw, dict):
        findings_raw = findings_raw.get("findings", []) or []

    findings = [ReviewFinding.from_dict(f) for f in findings_raw]
    res = ReviewReconciler.reconcile(findings)
    md_report = res.render_markdown()
    print(md_report)

    out_file = args.output
    if not out_file and args.run_dir:
        out_file = str(Path(args.run_dir) / "reconciliation_report.md")

    if out_file:
        Path(out_file).write_text(md_report, encoding="utf-8")
        print(f"\nSaved report to {out_file}")

    if res.unresolved_blockers > 0:
        return 1
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    """Executes a verification plan for a project or task."""
    project_dir = args.project_dir or "."
    context = ProjectAdapter.discover(project_dir)
    task_id = args.task_id or "VERIFY-RUN"

    plan = ProjectAdapter.create_verification_plan(context, task_id=task_id)
    print(f"Running verification plan for project '{context.name}' ({len(plan.steps)} steps)...")
    status = plan.execute_all(cwd=project_dir)

    for step in plan.steps:
        mark = "✓" if step.status == "verified" else "✗"
        interp_info = f" [using {step.interpreter}]" if step.interpreter else ""
        print(f"[{mark}] {step.name}: {step.status} (exit {step.exit_code}, {step.duration_seconds}s){interp_info}")
        if step.status == "failed" and step.stderr:
            print(f"    Error: {step.stderr.strip()[:200]}")

    print(f"\nOverall Verification Status: {status.upper()}")

    out_file = args.output
    if not out_file and args.run_dir:
        out_file = str(Path(args.run_dir) / "verification.json")

    if out_file:
        Path(out_file).parent.mkdir(parents=True, exist_ok=True)
        Path(out_file).write_text(plan.to_json(), encoding="utf-8")
        print(f"Saved verification output to {out_file}")

    return 0 if status == "passed" else 1


def cmd_record(args: argparse.Namespace) -> int:
    """Appends an event entry to the evidence ledger."""
    import json
    ledger = EvidenceLedger(args.ledger_file)
    findings_sum = None
    if args.findings_json:
        try:
            findings_sum = json.loads(args.findings_json)
        except Exception:
            pass

    meta = {}
    if args.failure_mode:
        meta["failure_mode"] = args.failure_mode
    if args.repository:
        meta["repository"] = args.repository
    if args.reviewer_role:
        meta["reviewer_role"] = args.reviewer_role

    entry = EvidenceEntry(
        task_id=args.task_id,
        agent_id=args.agent_id,
        action=args.action,
        command=args.command,
        result=args.result,
        artifact=args.artifact,
        task_class=args.task_class,
        risk_level=args.risk_level,
        reasoning_tier=args.reasoning_tier,
        implementing_agent=args.implementing_agent or args.actual_agent,
        recommended_agent=args.recommended_agent,
        actual_agent=args.actual_agent or args.implementing_agent,
        is_override=args.is_override,
        override_reason=args.override_reason,
        defect_type=args.defect_type,
        orchestration_action=args.orchestration_action,
        repository=args.repository,
        reviewing_agents=args.reviewing_agents,
        remediation_cycles=args.remediation_cycles,
        control_plane_caught_defect=args.defect_caught,
        findings_summary=findings_sum,
        metadata=meta,
    )
    ledger.append_entry(entry)
    print(f"Recorded evidence entry '{entry.entry_id}' for task '{entry.task_id}'.")
    return 0


def cmd_metrics(args: argparse.Namespace) -> int:
    """Calculates and displays engineering history metrics."""
    ledger = EvidenceLedger(args.ledger_file)
    entries = ledger.list_all_entries()
    summary = MetricsCalculator.calculate(entries)
    if getattr(args, "format", "markdown") == "json":
        import json
        print(json.dumps(summary.to_dict(), indent=2))
    else:
        print(summary.render_markdown())
    return 0


def cmd_boundary(args: argparse.Namespace) -> int:
    """Evaluates human authority boundaries for a task."""
    spec = TaskSpec.load_from_file(args.task_file)
    actions = args.actions or []
    res = HumanBoundaryGate.evaluate(spec, planned_actions=actions)

    if res.requires_human_approval and res.decision_packet:
        md = res.decision_packet.render_markdown()
        print(md)
        out_file = args.output
        if not out_file and getattr(args, "run_dir", None):
            out_file = str(Path(args.run_dir) / "decision_packet.md")
        if out_file:
            Path(out_file).parent.mkdir(parents=True, exist_ok=True)
            Path(out_file).write_text(md, encoding="utf-8")
            print(f"\nSaved decision packet to {out_file}")
        return 2  # Signal awaiting human
    else:
        print("✓ All actions within autonomous operating authority (no human boundary triggered).")
        return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="control_plane",
        description="Deterministic Multi-Agent Engineering Control Plane CLI",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Command to execute")

    # init-task
    p_init = subparsers.add_parser("init-task", help="Initialize a new task specification")
    p_init.add_argument("--task-id", required=True, help="Task ID (e.g. TASK-101)")
    p_init.add_argument("--repo", default=".", help="Repository path or name")
    p_init.add_argument("--objective", required=True, help="Task objective description")
    p_init.add_argument("--criteria", nargs="*", help="Acceptance criteria")
    p_init.add_argument("--constraints", nargs="*", help="Constraints")
    p_init.add_argument("--task-class", default="feature", help="Task class / category")
    p_init.add_argument("--risk", default="medium", choices=["low", "medium", "high", "critical"])
    p_init.add_argument("--skills", nargs="*", help="Required skills")
    p_init.add_argument("--tier", default="tier_2", choices=["tier_1", "tier_2", "tier_3"])
    p_init.add_argument("--preferred-agent", help="Preferred agent ID override")
    p_init.add_argument("--output", "-o", help="Output file path (YAML or JSON)")

    # route-task
    p_route = subparsers.add_parser("route-task", help="Route task to appropriate agent and reviewers")
    p_route.add_argument("--task-file", required=True, help="Path to task spec file")

    # briefs
    p_briefs = subparsers.add_parser("briefs", help="Generate independent reviewer briefs")
    p_briefs.add_argument("--task-file", required=True, help="Path to task spec file")
    p_briefs.add_argument("--diff-file", help="Path to diff file")
    p_briefs.add_argument("--roles", nargs="*", help="Specific reviewer roles to generate")
    p_briefs.add_argument("--output-dir", help="Output directory for briefs")

    # prepare-run
    p_prep = subparsers.add_parser("prepare-run", help="Prepare cross-agent dogfood task run artifacts")
    p_prep.add_argument("--task-file", required=True, help="Path to task spec file")
    p_prep.add_argument("--diff-file", help="Path to diff file")
    p_prep.add_argument("--roles", nargs="*", help="Specific reviewer roles to generate")
    p_prep.add_argument("--run-dir", help="Task run directory path")

    # reconcile
    p_rec = subparsers.add_parser("reconcile", help="Reconcile multi-agent review findings")
    p_rec.add_argument("--findings-file", required=True, help="YAML/JSON findings file")
    p_rec.add_argument("--output", "-o", help="Save markdown report to path")
    p_rec.add_argument("--run-dir", help="Task run directory path")

    # verify
    p_ver = subparsers.add_parser("verify", help="Execute project verification plan")
    p_ver.add_argument("--project-dir", default=".", help="Target project root directory")
    p_ver.add_argument("--task-id", help="Optional task ID")
    p_ver.add_argument("--output", "-o", help="Save verification JSON output to path")
    p_ver.add_argument("--run-dir", help="Task run directory path to store verification.json")

    # record
    p_rec_ev = subparsers.add_parser("record", help="Record evidence entry to ledger")
    p_rec_ev.add_argument("--task-id", required=True, help="Task ID")
    p_rec_ev.add_argument("--agent-id", required=True, help="Agent ID")
    p_rec_ev.add_argument("--action", required=True, help="Action performed")
    p_rec_ev.add_argument("--command", help="Command executed")
    p_rec_ev.add_argument("--result", help="Command result")
    p_rec_ev.add_argument("--artifact", help="Artifact produced")
    p_rec_ev.add_argument("--task-class", help="Task class")
    p_rec_ev.add_argument("--risk-level", help="Risk level")
    p_rec_ev.add_argument("--reasoning-tier", help="Reasoning tier")
    p_rec_ev.add_argument("--implementing-agent", help="Implementing agent ID")
    p_rec_ev.add_argument("--recommended-agent", help="Recommended agent ID")
    p_rec_ev.add_argument("--actual-agent", help="Actual implementing agent ID")
    p_rec_ev.add_argument("--is-override", action="store_true", help="Flag if routing was overridden")
    p_rec_ev.add_argument("--override-reason", help="Reason for human routing override")
    p_rec_ev.add_argument("--defect-type", choices=["review_caught_defect", "verification_caught_defect", "boundary_caught_risk"], help="Defect type caught by control plane")
    p_rec_ev.add_argument("--orchestration-action", help="Orchestration action for tracking human friction")
    p_rec_ev.add_argument("--repository", help="Repository name or path")
    p_rec_ev.add_argument("--reviewer-role", help="Reviewer role for caught defect provenance")
    p_rec_ev.add_argument("--reviewing-agents", nargs="*", help="Reviewing agent IDs")
    p_rec_ev.add_argument("--remediation-cycles", type=int, help="Remediation cycle count")
    p_rec_ev.add_argument("--defect-caught", action="store_true", help="Flag if control plane caught a defect")
    p_rec_ev.add_argument("--findings-json", help="JSON summary of findings")
    p_rec_ev.add_argument("--failure-mode", help="Failure mode string")
    p_rec_ev.add_argument("--ledger-file", help="Ledger file path")

    # metrics / report
    p_met = subparsers.add_parser("metrics", help="Calculate agent performance metrics")
    p_met.add_argument("--ledger-file", help="Ledger file path")
    p_met.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")

    p_rep = subparsers.add_parser("report", help="Display full operational summary report")
    p_rep.add_argument("--ledger-file", help="Ledger file path")
    p_rep.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")

    # boundary
    p_bound = subparsers.add_parser("check-boundary", help="Evaluate human authority boundary")
    p_bound.add_argument("--task-file", required=True, help="Path to task spec file")
    p_bound.add_argument("--actions", nargs="*", help="Planned actions or commands")
    p_bound.add_argument("--output", "-o", help="Save decision packet markdown to path")
    p_bound.add_argument("--run-dir", help="Task run directory path")

    return parser


def main(args: Optional[List[str]] = None) -> int:
    if args is None:
        args = sys.argv[1:]
    parser = build_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.subcommand:
        parser.print_help()
        return 1

    handlers = {
        "init-task": cmd_init_task,
        "route-task": cmd_route_task,
        "briefs": cmd_briefs,
        "prepare-run": cmd_prepare_run,
        "reconcile": cmd_reconcile,
        "verify": cmd_verify,
        "record": cmd_record,
        "metrics": cmd_metrics,
        "report": cmd_metrics,
        "check-boundary": cmd_boundary,
    }

    handler = handlers.get(parsed_args.subcommand)
    if handler:
        return handler(parsed_args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

