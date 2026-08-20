#!/usr/bin/env python3
"""
project_adapter.py

Boundary adapter that interfaces between the control plane and target project repositories.
The control plane provides orchestration; the project supplies local truth.
"""

from dataclasses import dataclass, field, asdict
import json
from pathlib import Path
from typing import Any, Dict, List, Union
import tomllib
import yaml

from src.control_plane.hygiene_policy import HygienePolicyClassifier
from src.control_plane.verification import VerificationPlan


from src.control_plane.task_spec import DataClassSerializationMixin


@dataclass
class ProjectContext(DataClassSerializationMixin):
    """Represents discovered local truth for a specific project repository."""

    project_root: str
    name: str
    project_types: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    test_commands: List[List[str]] = field(default_factory=list)
    build_commands: List[List[str]] = field(default_factory=list)
    lint_commands: List[List[str]] = field(default_factory=list)
    hygiene_commands: List[List[str]] = field(default_factory=list)
    hygiene_status: str = "not_configured"
    capabilities: List[str] = field(default_factory=list)
    has_manifest: bool = False
    has_agents_md: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProjectAdapter:
    """
    Discovers project configuration and constructs project-specific verification plans
    while respecting local project sovereignty.
    """

    @classmethod
    def discover(cls, project_dir: Union[str, Path] = ".") -> ProjectContext:
        """
        Scans a directory for .ai-project.toml, project_manifest.yaml, .slop/ configuration,
        or project stack markers.
        """
        root = Path(project_dir).resolve()
        name = root.name
        project_types: List[str] = []
        skills: List[str] = []
        test_commands: List[List[str]] = []
        build_commands: List[List[str]] = []
        lint_commands: List[List[str]] = []
        hygiene_commands: List[List[str]] = []
        hygiene_status = "not_configured"
        capabilities: List[str] = []
        has_manifest = False
        has_agents_md = (root / "AGENTS.md").exists()

        def _extract_manifest_cmds(cmds: Dict[str, Any]) -> None:
            for k in ("test", "build", "lint"):
                if k in cmds:
                    val = cmds[k]
                    cmd_list = val if isinstance(val, list) else [val]
                    if k == "test":
                        test_commands.append(cmd_list)
                    elif k == "build":
                        build_commands.append(cmd_list)
                    elif k == "lint":
                        lint_commands.append(cmd_list)
            for hk in ("hygiene", "repository_hygiene"):
                if hk in cmds:
                    hval = cmds[hk]
                    hygiene_commands.append(hval if isinstance(hval, list) else [hval])
                    break

        # 1. Check for .ai-project.toml
        ai_toml = root / ".ai-project.toml"
        if ai_toml.exists():
            has_manifest = True
            with open(ai_toml, "rb") as f:
                data = tomllib.load(f)
            name = data.get("name", name)
            project_types = data.get("project_type", [])
            skills = data.get("skills", [])
            _extract_manifest_cmds(data.get("commands", {}))
            sec = data.get("security", {})
            capabilities = sec.get("capabilities", [])

        # 2. Check for project_manifest.yaml
        manifest_yaml = root / "project_manifest.yaml"
        if manifest_yaml.exists() and not has_manifest:
            has_manifest = True
            with open(manifest_yaml, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            name = data.get("name", name)
            project_types = data.get("project_types", [])
            skills = data.get("skills", [])
            _extract_manifest_cmds(data.get("commands", {}))
            capabilities = data.get("capabilities", [])

        # 3. Discover SlopsLint repository hygiene configuration
        slop_config = root / ".slop" / "config.yml"
        slop_ceilings = root / ".slop" / "ceilings.yml"
        if slop_config.exists():
            if not slop_ceilings.exists():
                hygiene_status = "invalid_configuration"
            else:
                ok, _, pmeta = HygienePolicyClassifier.verify_provider_integrity("slopslint")
                if ok:
                    hygiene_status = "configured_and_passed"
                elif pmeta.get("status") == "version_mismatch":
                    hygiene_status = "invalid_provider_version"
                else:
                    hygiene_status = "configured_tool_missing"

            if not hygiene_commands:
                hygiene_commands.append(["slopslint", "check", "--classify", "--enforce"])

        # 4. Stack heuristics if commands are not explicitly specified
        if not test_commands and not build_commands:
            # Check for Makefile
            makefile = root / "Makefile"
            if makefile.exists():
                text = makefile.read_text(encoding="utf-8", errors="ignore")
                if "test:" in text:
                    test_commands.append(["make", "test"])
                if "lint:" in text:
                    lint_commands.append(["make", "lint"])
                if "build:" in text:
                    build_commands.append(["make", "build"])

            # Check for Go
            if (root / "go.mod").exists():
                if "go" not in project_types:
                    project_types.append("go")
                if not test_commands:
                    test_commands.append(["go", "test", "./..."])
                if not build_commands:
                    build_commands.append(["go", "build", "./..."])
                if not lint_commands:
                    lint_commands.append(["go", "vet", "./..."])

            # Check for Python
            if (root / "pyproject.toml").exists() or (root / "setup.py").exists() or (root / "requirements.txt").exists():
                if "python" not in project_types:
                    project_types.append("python")
                if not test_commands:
                    test_commands.append(["pytest"])
                if not lint_commands:
                    lint_commands.append(["flake8"])

            # Check for Node / TS
            if (root / "package.json").exists():
                if "javascript" not in project_types:
                    project_types.append("javascript")
                if not test_commands:
                    test_commands.append(["npm", "test"])

            # Check for Rust
            if (root / "Cargo.toml").exists():
                if "rust" not in project_types:
                    project_types.append("rust")
                if not test_commands:
                    test_commands.append(["cargo", "test"])
                if not build_commands:
                    build_commands.append(["cargo", "build"])

            # Check for standalone shell test suites
            tests_dir = root / "tests"
            if tests_dir.is_dir() and not test_commands:
                sh_tests = sorted(tests_dir.glob("*.sh"))
                for sh_t in sh_tests:
                    rel_p = str(sh_t.relative_to(root))
                    test_commands.append(["bash", rel_p])

        return ProjectContext(
            project_root=str(root),
            name=name,
            project_types=project_types,
            skills=skills,
            test_commands=test_commands,
            build_commands=build_commands,
            lint_commands=lint_commands,
            hygiene_commands=hygiene_commands,
            hygiene_status=hygiene_status,
            capabilities=capabilities,
            has_manifest=has_manifest,
            has_agents_md=has_agents_md,
        )

    @classmethod
    def create_verification_plan(cls, context: ProjectContext, task_id: str) -> VerificationPlan:
        """
        Creates a VerificationPlan tailored to the project's discovered commands.
        """
        plan = VerificationPlan(task_id=task_id)
        idx = 1

        for cmd in context.lint_commands:
            plan.add_step(
                step_id=f"step-{idx:02d}",
                name=f"Lint check ({' '.join(cmd)})",
                command=cmd,
                category="lint",
                required=True,
            )
            idx += 1

        for cmd in context.build_commands:
            plan.add_step(
                step_id=f"step-{idx:02d}",
                name=f"Build check ({' '.join(cmd)})",
                command=cmd,
                category="build",
                required=True,
            )
            idx += 1

        for cmd in context.test_commands:
            plan.add_step(
                step_id=f"step-{idx:02d}",
                name=f"Automated test suite ({' '.join(cmd)})",
                command=cmd,
                category="unit_test",
                required=True,
            )
            idx += 1

        for cmd in context.hygiene_commands:
            plan.add_step(
                step_id=f"step-{idx:02d}",
                name=f"Repository hygiene gate ({' '.join(cmd)})",
                command=cmd,
                category="repository_hygiene",
                required=True,
            )
            idx += 1

        return plan
