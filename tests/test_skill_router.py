import os

import pytest

from src.core.skill_router import SkillRouter
from src.infrastructure.build_vector_index import VectorIndexBuilder


def write_skill(base_dir, name, description, triggers=None, body="Directives here."):
    skill_dir = os.path.join(base_dir, name)
    os.makedirs(skill_dir, exist_ok=True)
    frontmatter = [f'name: "{name}"', f'description: "{description}"']
    if triggers:
        frontmatter.append("triggers:")
        frontmatter.extend(f'  - "{t}"' for t in triggers)
    content = "---\n" + "\n".join(frontmatter) + f"\n---\n\n# {name}\n\n{body}\n"
    path = os.path.join(skill_dir, "SKILL.md")
    with open(path, "w", encoding="utf8") as f:
        f.write(content)
    return path


@pytest.fixture
def skills_dir(tmp_path):
    base = str(tmp_path / "skills")
    write_skill(
        base,
        "l4d2_scripting",
        "VScript and SourcePawn scripting for Left 4 Dead 2.",
        triggers=["l4d2", "left 4 dead"],
    )
    write_skill(
        base,
        "baseball_analytics",
        "Sabermetrics, statistical modeling, and baseball strategy.",
    )
    write_skill(
        base,
        "devops",
        "CI CD pipeline creation, containerization, and infrastructure deployment.",
    )
    return base


@pytest.fixture
def router(skills_dir):
    r = SkillRouter(skills_dir=skills_dir)
    # Force the keyword fallback so tests never download the cross encoder.
    r._scorer_failed = True
    return r


def test_loads_skills_with_frontmatter(router):
    names = {s.name for s in router.skills}
    assert names == {"l4d2_scripting", "baseball_analytics", "devops"}
    l4d2 = next(s for s in router.skills if s.name == "l4d2_scripting")
    assert "l4d2" in l4d2.triggers


def test_ignores_files_without_frontmatter(tmp_path):
    base = str(tmp_path / "skills")
    skill_dir = os.path.join(base, "broken")
    os.makedirs(skill_dir)
    with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
        f.write("# No frontmatter here\n")
    router = SkillRouter(skills_dir=base)
    assert router.skills == []


def test_trigger_match_routes_deterministically(router):
    routed = router.route("Write a VScript mutation for my l4d2 server")
    names = [skill.name for skill, _, _ in routed]
    assert "l4d2_scripting" in names
    reason = next(r for skill, _, r in routed if skill.name == "l4d2_scripting")
    assert "trigger" in reason


def test_semantic_fallback_matches_keyword_overlap(router):
    routed = router.route("Help me with sabermetrics and baseball statistical modeling")
    names = [skill.name for skill, _, _ in routed]
    assert "baseball_analytics" in names


def test_unrelated_prompt_routes_nothing(router):
    routed = router.route("What is the capital of France?")
    assert routed == []


def test_disabled_router_returns_nothing(router):
    router.enabled = False
    assert router.route("l4d2 scripting question") == []
    assert router.build_context("l4d2 scripting question") == ""


def test_build_context_injects_full_body(router):
    context = router.build_context("Fix my l4d2 vscript")
    assert "l4d2_scripting" in context
    assert "Directives here." in context


def test_build_context_respects_budget(router):
    router.max_context_chars = 40
    context = router.build_context("Fix my l4d2 vscript")
    # Too small for the body, so only the description summary fits at most.
    assert "Directives here." not in context


def test_missing_skills_dir_is_empty(tmp_path):
    router = SkillRouter(skills_dir=str(tmp_path / "does_not_exist"))
    assert router.skills == []
    assert router.route("anything") == []


def test_index_scan_includes_dot_agents(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    skill_dir = repo / ".agents" / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: demo\n---\n\nDemo skill body.")
    (repo / "README.md").write_text("Readme content.")

    builder = VectorIndexBuilder()
    builder.repo_root = str(repo)
    builder.docs_to_insert = []
    builder.metadata_to_insert = []
    builder.ids_to_insert = []
    builder.scan_files()

    sources = {m["source"] for m in builder.metadata_to_insert}
    assert any(".agents" in s for s in sources), sources
    assert any("README.md" in s for s in sources), sources
