import os

from scripts.generate_skills_manifest import sync_claude_skills_dir


def _make_skill_dir(base, name):
    skill_dir = os.path.join(base, name)
    os.makedirs(skill_dir, exist_ok=True)
    with open(os.path.join(skill_dir, "SKILL.md"), "w", encoding="utf8") as f:
        f.write(f"---\nname: \"{name}\"\ndescription: \"test\"\n---\n\nBody.\n")


def test_builds_symlinks_for_skills_and_skill_commands(tmp_path):
    repo_root = str(tmp_path)
    _make_skill_dir(os.path.join(repo_root, ".agents", "skills"), "cyber_security")
    _make_skill_dir(os.path.join(repo_root, ".agents", "skills"), "blue_team")
    _make_skill_dir(os.path.join(repo_root, ".agents", "skill_commands"), "work_next_item")

    sync_claude_skills_dir(repo_root)

    target_dir = os.path.join(repo_root, ".claude", "skills")
    assert os.path.isdir(target_dir) and not os.path.islink(target_dir)
    assert set(os.listdir(target_dir)) == {"cyber_security", "blue_team", "work_next_item"}

    for name, source_root in (
        ("cyber_security", "skills"),
        ("blue_team", "skills"),
        ("work_next_item", "skill_commands"),
    ):
        link_path = os.path.join(target_dir, name)
        assert os.path.islink(link_path)
        assert os.path.isfile(os.path.join(link_path, "SKILL.md"))
        target = os.readlink(link_path)
        assert target == os.path.join("..", "..", ".agents", source_root, name)


def test_converts_old_single_symlink_layout(tmp_path):
    repo_root = str(tmp_path)
    _make_skill_dir(os.path.join(repo_root, ".agents", "skills"), "cyber_security")
    os.makedirs(os.path.join(repo_root, ".claude"), exist_ok=True)
    old_link = os.path.join(repo_root, ".claude", "skills")
    os.symlink(os.path.join("..", ".agents", "skills"), old_link)
    assert os.path.islink(old_link)

    sync_claude_skills_dir(repo_root)

    assert os.path.isdir(old_link) and not os.path.islink(old_link)
    assert os.path.islink(os.path.join(old_link, "cyber_security"))


def test_removes_stale_entries(tmp_path):
    repo_root = str(tmp_path)
    _make_skill_dir(os.path.join(repo_root, ".agents", "skills"), "cyber_security")

    target_dir = os.path.join(repo_root, ".claude", "skills")
    os.makedirs(target_dir, exist_ok=True)
    stale_link = os.path.join(target_dir, "removed_skill")
    os.symlink(os.path.join("..", "..", ".agents", "skills", "removed_skill"), stale_link)

    sync_claude_skills_dir(repo_root)

    assert not os.path.lexists(stale_link)
    assert os.listdir(target_dir) == ["cyber_security"]


def test_missing_skill_commands_dir_does_not_crash(tmp_path):
    repo_root = str(tmp_path)
    _make_skill_dir(os.path.join(repo_root, ".agents", "skills"), "cyber_security")
    # .agents/skill_commands/ deliberately absent.

    sync_claude_skills_dir(repo_root)

    target_dir = os.path.join(repo_root, ".claude", "skills")
    assert os.listdir(target_dir) == ["cyber_security"]
