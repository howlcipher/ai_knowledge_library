import json
import os

from scripts.library_statistics import LibraryStatisticsGenerator

FIRST_BADGE = (
    '<img src="https://img.shields.io/static/v1?label=SYS_CORE&message=Active'
    '&color=00f0ff&style=for_the_badge" alt="AI Library Badge" />'
)


def _make_repo(tmp_path, skills, readme_body):
    repo_root = str(tmp_path)
    os.makedirs(os.path.join(repo_root, ".agents"), exist_ok=True)
    with open(os.path.join(repo_root, ".agents", "skills.json"), "w") as f:
        json.dump({"version": 1, "skills": skills}, f)
    with open(os.path.join(repo_root, "README.md"), "w") as f:
        f.write(readme_body)
    return repo_root


def test_count_skills_reads_skill_manifest_length(tmp_path):
    repo_root = _make_repo(
        tmp_path, skills=["a", "b", "c"], readme_body=f"{FIRST_BADGE}\n"
    )
    generator = LibraryStatisticsGenerator(repo_root=repo_root)

    assert generator.count_skills() == 3


def test_update_readme_substitutes_existing_badge_message(tmp_path):
    existing_badge = (
        '<img src="https://img.shields.io/static/v1?label=Neural_Nodes&message=999'
        '&color=00ff41&style=for_the_badge" alt="Neural Nodes Badge" />'
    )
    repo_root = _make_repo(
        tmp_path, skills=["a", "b"], readme_body=f"{FIRST_BADGE}\n{existing_badge}\n"
    )
    generator = LibraryStatisticsGenerator(repo_root=repo_root)

    generator.update_readme(2)

    content = open(generator.readme_path).read()
    assert "message=999" not in content
    assert (
        '<img src="https://img.shields.io/static/v1?label=Neural_Nodes&message=2'
        '&color=00ff41&style=for_the_badge" alt="Neural Nodes Badge" />' in content
    )


def test_update_readme_inserts_badge_when_missing(tmp_path):
    repo_root = _make_repo(tmp_path, skills=["a"], readme_body=f"{FIRST_BADGE}\n")
    generator = LibraryStatisticsGenerator(repo_root=repo_root)

    generator.update_readme(1)

    content = open(generator.readme_path).read()
    assert (
        '<img src="https://img.shields.io/static/v1?label=Neural_Nodes&message=1'
        '&color=00ff41&style=for_the_badge" alt="Neural Nodes Badge" />' in content
    )


def test_update_readme_is_idempotent_on_repeated_runs(tmp_path):
    repo_root = _make_repo(tmp_path, skills=["a"], readme_body=f"{FIRST_BADGE}\n")
    generator = LibraryStatisticsGenerator(repo_root=repo_root)

    generator.update_readme(1)
    generator.update_readme(1)

    content = open(generator.readme_path).read()
    assert content.count("label=Neural_Nodes") == 1
