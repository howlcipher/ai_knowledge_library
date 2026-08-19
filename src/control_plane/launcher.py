#!/usr/bin/env python3
"""
launcher.py

Thin global entrypoint into the Multi-Agent Engineering Control Plane.
Operates across any target Git repository, discovering project-local truth
while enforcing global control plane policies, deterministic routing,
independent reviewer selection, verification planning, and fail-closed
human authority boundaries.
"""

import argparse
import hashlib
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import List, Optional, Tuple, Union

from src.control_plane.cli import cmd_doctor as cp_cmd_doctor, cmd_verify as cp_cmd_verify
from src.control_plane.evidence_ledger import EvidenceEntry, EvidenceLedger
from src.control_plane.human_boundary import HumanBoundaryGate
from src.control_plane.project_adapter import ProjectAdapter, ProjectContext
from src.control_plane.reviewers import get_reviewer_role
from src.control_plane.router import TaskRouter, RoutingDecision
from src.control_plane.task_spec import TaskSpec


class ControlPlaneError(Exception):
    """Base exception for control plane launcher errors."""
    pass


class TargetRepositoryNotFoundError(ControlPlaneError):
    """Raised when no valid Git target repository is discovered."""
    pass


class ControlPlaneNotFoundError(ControlPlaneError):
    """Raised when ai_knowledge_library cannot be located."""
    pass


def find_git_repo_root(start_dir: Optional[Union[str, Path]] = None) -> Path:
    """Discovers the root directory of the current Git repository using `git rev-parse`."""
    target = Path(start_dir or os.getcwd()).resolve()
    try:
        res = subprocess.run(
            ["git", "-C", str(target), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            return Path(res.stdout.strip()).resolve()
    except Exception:
        pass

    curr = target
    while curr != curr.parent:
        if (curr / ".git").exists():
            return curr
        curr = curr.parent

    raise TargetRepositoryNotFoundError(
        f"ERROR: no target Git repository found in '{target}'. 'ai' must be executed inside a Git repository."
    )


def find_control_plane_root(override_path: Optional[str] = None) -> Path:
    """Discovers the ai_knowledge_library repository path using the 5-step precedence."""
    if override_path:
        p = Path(override_path).expanduser().resolve()
        if (p / "src" / "control_plane").is_dir() or (p / "AGENTS.md").is_file():
            return p
        raise ControlPlaneNotFoundError(
            f"ERROR: specified ai_knowledge_library control plane path does not exist: {override_path}"
        )

    env_path = os.environ.get("AI_KNOWLEDGE_LIBRARY")
    if env_path:
        p = Path(env_path).expanduser().resolve()
        if (p / "src" / "control_plane").is_dir() or (p / "AGENTS.md").is_file():
            return p
        raise ControlPlaneNotFoundError(
            f"ERROR: AI_KNOWLEDGE_LIBRARY environment variable points to invalid path: {env_path}"
        )

    candidates = [
        Path.home() / ".config" / "ai-control-plane" / "config.toml",
        Path.home() / ".config" / "ai" / "config.toml",
    ]
    for cfg in candidates:
        if cfg.is_file():
            try:
                txt = cfg.read_text(encoding="utf-8")
                match = re.search(r'path\s*=\s*["\']([^"\']+)["\']', txt)
                if match:
                    p = Path(match.group(1)).expanduser().resolve()
                    if (p / "src" / "control_plane").is_dir() or (p / "AGENTS.md").is_file():
                        return p
                    raise ControlPlaneNotFoundError(f"ERROR: configured path in '{cfg}' is invalid: {match.group(1)}")
            except ControlPlaneNotFoundError:
                raise
            except Exception:
                pass

    self_root = Path(__file__).resolve().parent.parent.parent
    if (self_root / "src" / "control_plane").is_dir() and (self_root / "AGENTS.md").is_file():
        return self_root

    raise ControlPlaneNotFoundError(
        "ERROR: configured ai_knowledge_library control plane not found.\n"
        "Please set the AI_KNOWLEDGE_LIBRARY environment variable or configure ~/.config/ai-control-plane/config.toml:\n\n"
        "  [control_plane]\n"
        "  path = \"/path/to/ai_knowledge_library\"\n"
    )


def infer_task_metadata(
    objective: str,
    repo_name: str,
    explicit_id: Optional[str] = None,
    explicit_risk: Optional[str] = None,
    explicit_tier: Optional[str] = None,
    explicit_class: Optional[str] = None,
) -> Tuple[str, str, str, str]:
    """Infers task ID, task class, risk level, and reasoning tier from objective text."""
    clean_obj = objective.strip()
    lowered = clean_obj.lower()

    if explicit_id:
        task_id = explicit_id
    else:
        issue_match = re.search(r'(?:issue|bug|item|task)\s*#?\s*([A-Za-z0-9_-]+)', clean_obj, re.IGNORECASE)
        if issue_match:
            issue_val = issue_match.group(1).upper()
            if issue_val.startswith("TASK-") or issue_val.startswith("IMP-") or issue_val.startswith("ISSUE-"):
                task_id = issue_val
            else:
                pfx = re.sub(r'[^A-Za-z0-9]', '', repo_name).upper()[:8] or "TASK"
                task_id = f"{pfx}-{issue_val}"
        else:
            h_suf = hashlib.sha256(f"{repo_name}:{clean_obj}".encode("utf-8")).hexdigest()[:6].upper()
            pfx = re.sub(r'[^A-Za-z0-9]', '', repo_name).upper()[:8] or "TASK"
            task_id = f"{pfx}-{h_suf}"

    if explicit_class:
        task_class = explicit_class
    elif any(k in lowered for k in ["security", "vuln", "auth", "cve", "patch", "exploit"]):
        task_class = "security_patch"
    elif any(k in lowered for k in ["fix", "bug", "crash", "error", "defect", "broken", "fail"]):
        task_class = "bug_fix"
    elif any(k in lowered for k in ["refactor", "clean", "simplify", "restructure"]):
        task_class = "refactor"
    elif any(k in lowered for k in ["test", "falsif", "mock", "assert", "coverage"]):
        task_class = "test"
    elif any(k in lowered for k in ["doc", "readme", "comment", "guide"]):
        task_class = "documentation"
    elif any(k in lowered for k in ["deploy", "infra", "terraform", "helm", "k8s", "docker"]):
        task_class = "infrastructure"
    else:
        task_class = "feature"

    if explicit_risk:
        risk_level = explicit_risk
    elif any(k in lowered for k in ["critical", "production", "deploy", "terraform apply", "drop table", "credential", "secret"]):
        risk_level = "critical"
    elif any(k in lowered for k in ["security", "vuln", "auth", "boundary", "migration", "k8s", "ingress", "infra"]):
        risk_level = "high"
    elif any(k in lowered for k in ["doc", "typo", "readme", "comment", "format", "style", "lint"]):
        risk_level = "low"
    else:
        risk_level = "medium"

    if explicit_tier:
        reasoning_tier = explicit_tier
    elif risk_level in ("high", "critical") or task_class in ("security_patch", "infrastructure"):
        reasoning_tier = "tier_1"
    elif risk_level == "low" and task_class == "documentation":
        reasoning_tier = "tier_3"
    else:
        reasoning_tier = "tier_2"

    return task_id, task_class, risk_level, reasoning_tier


def format_agent_launch_command(agent_id: str, spec: TaskSpec, run_dir: Path, target_repo: Path) -> str:
    """Generates the exact recommended agent launch command for the selected agent."""
    t_path = run_dir / "task.yaml"
    rel_p = str(t_path.relative_to(target_repo)) if t_path.is_relative_to(target_repo) else str(t_path)
    
    if agent_id == "agy":
        return f'agy -p "Task: {spec.task_id} - {spec.objective}. Review task spec at {rel_p} and execute." --mode accept-edits'
    elif agent_id == "claude_code":
        return f'claude "Execute governed task {spec.task_id}: {spec.objective} using control plane spec at {rel_p}"'
    elif agent_id == "codex":
        return f'codex "Execute task {spec.task_id}: {spec.objective} per {rel_p}"'
    elif agent_id == "devin_cli":
        return f'devin run --task-file {rel_p}'
    elif agent_id == "local_ollama":
        return f'ollama run qwen2.5-coder:32b "Task {spec.task_id}: {spec.objective}"'
    return f'# Launch {agent_id} for task spec at {rel_p}'


def create_task_plan(
    ctx: ProjectContext,
    target_repo: Path,
    cp_root: Optional[Path],
    args: argparse.Namespace,
) -> Tuple[TaskSpec, RoutingDecision]:
    """Helper that constructs and routes a TaskSpec from CLI arguments."""
    tid, tclass, risk, tier = infer_task_metadata(
        objective=args.objective,
        repo_name=ctx.name,
        explicit_id=getattr(args, "task_id", None),
        explicit_risk=getattr(args, "risk", None),
        explicit_tier=getattr(args, "tier", None),
        explicit_class=getattr(args, "task_class", None),
    )
    skills = list(dict.fromkeys(ctx.skills + (getattr(args, "skills", None) or ["software_development"])))
    meta = {"target_repo_path": str(target_repo)}
    if cp_root:
        meta["control_plane_path"] = str(cp_root)

    spec = TaskSpec(
        task_id=tid,
        repository=ctx.name,
        objective=args.objective,
        acceptance_criteria=getattr(args, "criteria", None) or [f"Complete objective: {args.objective}", "Pass deterministic verification suite"],
        constraints=getattr(args, "constraints", None) or ["Adhere to project AGENTS.md and control plane policies"],
        task_class=tclass,
        risk_level=risk,
        required_skills=skills,
        recommended_reasoning_tier=tier,
        preferred_agent=getattr(args, "agent", None),
        metadata=meta,
    )
    decision = TaskRouter().route(spec)
    return spec, decision


def cmd_work(args: argparse.Namespace) -> int:
    """Executes the governed work command from any target repository."""
    target_repo = find_git_repo_root(args.repo)
    cp_root = find_control_plane_root(args.control_plane_dir)

    if not getattr(args, "skip_doctor", False):
        from src.infrastructure.doctor import check_dependencies, check_git_status
        dep_res = check_dependencies()
        if dep_res.status == "error" and not getattr(args, "force", False):
            print(f"ERROR: control-plane preflight failed: {dep_res.message}", file=sys.stderr)
            return 1
        git_res = check_git_status(target_repo)
        if git_res.status == "error" and not getattr(args, "force", False):
            print(f"ERROR: target repository preflight failed: {git_res.message}", file=sys.stderr)
            return 1

    ctx = ProjectAdapter.discover(target_repo)
    spec, decision = create_task_plan(ctx, target_repo, cp_root, args)

    run_dir = target_repo / ".task_runs" / spec.task_id
    reviews_dir = run_dir / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)
    spec.save_to_file(str(run_dir / "task.yaml"))

    for role_id in decision.recommended_reviewers:
        role = get_reviewer_role(role_id)
        if role:
            (reviews_dir / f"{role_id}.md").write_text(role.render_brief(task=spec, diff_content=""), encoding="utf-8")

    (run_dir / "findings_template.yaml").write_text("# Review Findings Template\nfindings: []\n", encoding="utf-8")

    plan = ProjectAdapter.create_verification_plan(ctx, task_id=spec.task_id)
    (run_dir / "verification_plan.json").write_text(plan.to_json(), encoding="utf-8")

    planned_actions = getattr(args, "actions", None) or []
    if any(kw in args.objective.lower() for kw in ["deploy", "terraform apply", "kubectl apply", "drop table"]):
        planned_actions.append(args.objective)
    boundary_res = HumanBoundaryGate.evaluate(spec, planned_actions=planned_actions, verification=plan)

    ev = EvidenceEntry(
        task_id=spec.task_id,
        agent_id=decision.selected_agent_id,
        action="task_created",
        repository=ctx.name,
        task_class=spec.task_class,
        risk_level=spec.risk_level,
        reasoning_tier=decision.reasoning_tier,
        metadata={"target_repo": str(target_repo)},
    )
    if decision.is_override:
        ev.is_override = True
        ev.override_reason = decision.override_reason
    EvidenceLedger(str(cp_root / "logs" / "control_plane" / "evidence_ledger.jsonl")).append_entry(ev)

    launch_cmd = format_agent_launch_command(decision.selected_agent_id, spec, run_dir, target_repo)

    print("=" * 60)
    print("AI ENGINEERING CONTROL PLANE — TASK INITIALIZED")
    print("=" * 60)
    print(f"Target Repository:    {target_repo} ({ctx.name})")
    print(f"Project Stack:        {', '.join(ctx.project_types) or 'generic'}")
    print(f"Project AGENTS.md:    {'Present' if ctx.has_agents_md else 'Not found (using global policy)'}")
    print(f"Hygiene Policy:       {ctx.hygiene_status}")
    print(f"Task ID:              {spec.task_id}")
    print(f"Objective:            {spec.objective}")
    print(f"Risk Level:           {spec.risk_level.upper()}")
    print(f"Reasoning Tier:       {decision.reasoning_tier}")
    if decision.is_override:
        print(f"Override Note:        {decision.override_reason}")
    print("-" * 60)
    print("TASK ROUTING DECISION:")
    print(f"Selected Agent:       {decision.selected_agent_name} (`{decision.selected_agent_id}`)")
    print(f"Rationale:            {decision.rationale}")
    print(f"Reviewer Roles:       {', '.join(decision.recommended_reviewers)}")
    print("-" * 60)
    print("DETERMINISTIC VERIFICATION PLAN:")
    if plan.steps:
        for idx, s in enumerate(plan.steps, 1):
            print(f"  {idx}. [{s.category}] {s.name}")
    else:
        print("  (No automatic test/build steps discovered)")
    print("-" * 60)
    print("HUMAN AUTHORITY BOUNDARY:")
    if boundary_res.requires_human_approval:
        print("  🛑 AWAITING HUMAN APPROVAL (Boundary Triggered)")
        for b in boundary_res.triggered_boundaries:
            print(f"     - Boundary: {b}")
        if boundary_res.decision_packet:
            dp_path = run_dir / "decision_packet.md"
            dp_path.write_text(boundary_res.decision_packet.render_markdown(), encoding="utf-8")
            print(f"     - Decision packet written to: {dp_path}")
    else:
        print("  ✓ All actions within Autonomous Operating Authority")
    print("-" * 60)
    print("RUN ARTIFACTS PREPARED:")
    print(f"Run Directory:        {run_dir}")
    print(f"- Task Spec:          {run_dir / 'task.yaml'}")
    print(f"- Review Briefs:      {reviews_dir}/ ({len(decision.recommended_reviewers)} briefs)")
    print(f"- Findings Template:  {run_dir / 'findings_template.yaml'}")
    print(f"- Verification Plan:  {run_dir / 'verification_plan.json'}")
    print("-" * 60)
    print("RECOMMENDED AGENT LAUNCH COMMAND:")
    print(f"  {launch_cmd}")
    print("=" * 60)

    if getattr(args, "execute", False):
        if boundary_res.requires_human_approval:
            print("\nCannot auto-execute task requiring human authorization.", file=sys.stderr)
            return 2
        print(f"\nLaunching agent ({decision.selected_agent_id}) in {target_repo}...")
        try:
            cmd_args = shlex.split(launch_cmd)
            res = subprocess.run(cmd_args, cwd=str(target_repo), check=False)
            return res.returncode
        except Exception as exc:
            print(f"Error launching agent: {exc}", file=sys.stderr)
            return 1

    return 2 if boundary_res.requires_human_approval else 0


def cmd_route(args: argparse.Namespace) -> int:
    """Lightweight read-only routing of an objective against the current target repository."""
    target_repo = find_git_repo_root(args.repo)
    ctx = ProjectAdapter.discover(target_repo)
    spec, decision = create_task_plan(ctx, target_repo, None, args)

    print("=" * 60)
    print(f"TASK ROUTING DECISION: {spec.task_id}")
    print("=" * 60)
    print(f"Target Repository: {target_repo} ({ctx.name})")
    print(f"Objective:         {spec.objective}")
    print(f"Selected Agent:    {decision.selected_agent_name} (`{decision.selected_agent_id}`)")
    print(f"Reasoning Tier:    {decision.reasoning_tier}")
    print(f"Is Override:       {decision.is_override}")
    print(f"Rationale:         {decision.rationale}")
    print(f"Reviewers:         {', '.join(decision.recommended_reviewers)}")
    if decision.alternatives:
        print(f"Alternatives:      {', '.join(decision.alternatives)}")
    print("=" * 60)
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    """Executes workspace health diagnostics by delegating to control plane doctor."""
    target_repo = find_git_repo_root(args.repo)
    args.repo_dir = str(target_repo)
    return cp_cmd_doctor(args)


def cmd_verify(args: argparse.Namespace) -> int:
    """Executes deterministic project verification by delegating to control plane verify."""
    target_repo = find_git_repo_root(args.repo)
    args.project_dir = str(target_repo)
    args.output = None
    args.run_dir = None
    return cp_cmd_verify(args)


def cmd_status(args: argparse.Namespace) -> int:
    """Displays project status, active task runs, and hygiene metrics for the target repository."""
    target_repo = find_git_repo_root(args.repo)
    cp_root = find_control_plane_root(args.control_plane_dir)
    ctx = ProjectAdapter.discover(target_repo)

    print("=" * 60)
    print(f"AI CONTROL PLANE — PROJECT STATUS: {ctx.name}")
    print("=" * 60)
    print(f"Repository Path:    {target_repo}")
    print(f"Control Plane:      {cp_root}")
    print(f"Project Stack:      {', '.join(ctx.project_types) or 'generic'}")
    print(f"Project AGENTS.md:  {'Present' if ctx.has_agents_md else 'Not found'}")
    print(f"Hygiene Status:     {ctx.hygiene_status}")
    print("-" * 60)
    print("VERIFICATION COMMANDS DISCOVERED:")
    plan = ProjectAdapter.create_verification_plan(ctx, task_id="STATUS-CHECK")
    if plan.steps:
        for idx, s in enumerate(plan.steps, 1):
            print(f"  {idx}. [{s.category}] {' '.join(s.command)}")
    else:
        print("  (No automatic test/build commands detected)")

    task_runs_dir = target_repo / ".task_runs"
    runs = []
    if task_runs_dir.is_dir():
        runs = [d.name for d in task_runs_dir.iterdir() if d.is_dir() and (d / "task.yaml").exists()]

    print("-" * 60)
    print(f"ACTIVE TASK RUNS ({len(runs)}):")
    if runs:
        for r in sorted(runs):
            t_file = task_runs_dir / r / "task.yaml"
            try:
                t_spec = TaskSpec.load_from_file(str(t_file))
                print(f"  - {r}: [{t_spec.current_state}] {t_spec.objective} (Risk: {t_spec.risk_level})")
            except Exception:
                print(f"  - {r}")
    else:
        print("  (No task runs in .task_runs/)")

    journal_dir = target_repo / "documentation" / "task_journals"
    journals = []
    if journal_dir.is_dir():
        journals = [f.name for f in journal_dir.glob("*.md") if f.name != "TEMPLATE.md"]

    if journals:
        print("-" * 60)
        print(f"TASK JOURNALS ({len(journals)}):")
        for j in sorted(journals):
            print(f"  - {j}")

    print("=" * 60)
    return 0


def build_parser() -> argparse.ArgumentParser:
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "--control-plane-dir",
        "-C",
        help="Explicit path to ai_knowledge_library repository",
    )
    common_parser.add_argument(
        "--repo",
        "-R",
        help="Target Git repository directory (defaults to current working directory discovery)",
    )

    task_base_parser = argparse.ArgumentParser(add_help=False)
    task_base_parser.add_argument("objective", help="Task objective or description")
    task_base_parser.add_argument("--task-id", help="Explicit task ID")
    task_base_parser.add_argument("--risk", choices=["low", "medium", "high", "critical"], help="Risk level override")
    task_base_parser.add_argument("--tier", choices=["tier_1", "tier_2", "tier_3"], help="Reasoning tier override")
    task_base_parser.add_argument("--agent", help="Preferred agent override")

    parser = argparse.ArgumentParser(
        prog="ai",
        description="Thin Global Entrypoint into the Multi-Agent Engineering Control Plane",
        parents=[common_parser],
    )

    subparsers = parser.add_subparsers(dest="subcommand", help="Command to execute")

    p_work = subparsers.add_parser(
        "work",
        parents=[common_parser, task_base_parser],
        help="Run governed control-plane workflow on current repository",
    )
    p_work.add_argument("--task-class", help="Task class")
    p_work.add_argument("--criteria", nargs="*", help="Acceptance criteria list")
    p_work.add_argument("--constraints", nargs="*", help="Constraints list")
    p_work.add_argument("--actions", nargs="*", help="Planned actions for authority boundary checks")
    p_work.add_argument("--execute", "-x", action="store_true", help="Launch recommended agent CLI")
    p_work.add_argument("--dry-run", action="store_true", help="Generate plan without launching")
    p_work.add_argument("--skip-doctor", action="store_true", help="Skip preflight diagnostics")
    p_work.add_argument("--force", action="store_true", help="Proceed even if preflight has warnings")

    subparsers.add_parser(
        "route",
        parents=[common_parser, task_base_parser],
        help="Route an objective against the current repository",
    )

    subparsers.add_parser("doctor", parents=[common_parser], help="Run workspace health diagnostics")
    subparsers.add_parser("status", parents=[common_parser], help="Show project status and verification plan")

    p_ver = subparsers.add_parser("verify", parents=[common_parser], help="Execute deterministic verification plan")
    p_ver.add_argument("--task-id", help="Task ID")

    return parser


def main(args: Optional[List[str]] = None) -> int:
    p = build_parser()
    opts = p.parse_args(args if args is not None else sys.argv[1:])
    if not opts.subcommand:
        p.print_help()
        return 1

    actions = {
        "work": cmd_work,
        "route": cmd_route,
        "doctor": cmd_doctor,
        "status": cmd_status,
        "verify": cmd_verify,
    }
    fn = actions.get(opts.subcommand)
    if not fn:
        p.print_help()
        return 1

    try:
        return fn(opts)
    except ControlPlaneError as err:
        print(str(err), file=sys.stderr)
        return 1
    except Exception as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
