import subprocess
from pathlib import Path


def test_no_nested_mirror_paths_tracked():
    """
    Ensure that no nested mirror paths (docs/documentation/documentation/,
    docs/.agents/.agents/, docs/assets/assets/) are tracked in git, as these
    nested trees were residue of an old Makefile recipe bug and must not return.
    """
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        ["git", "ls-files", "docs"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    tracked_paths = result.stdout.strip().splitlines()
    for path in tracked_paths:
        assert not path.startswith("docs/documentation/documentation/")
        assert not path.startswith("docs/.agents/.agents/")
        assert not path.startswith("docs/assets/assets/")


def test_docs_target_cleans_mirrors_before_copy():
    """
    Verify that the 'docs' target in Makefile first removes existing mirrors
    (docs/documentation and docs/.agents) with 'rm -rf' before copying new content
    with 'cp -r documentation'. This keeps the mirror free of stale and nested files.
    """
    repo_root = Path(__file__).resolve().parents[1]
    makefile_path = repo_root / "Makefile"
    with makefile_path.open() as f:
        lines = f.readlines()

    docs_recipe_lines = []
    in_docs_recipe = False
    for line in lines:
        line = line.rstrip()
        if line.startswith("docs:"):
            in_docs_recipe = True
            continue
        if in_docs_recipe:
            if not line or (not line.startswith("\t") and not line.startswith("#")):
                break
            docs_recipe_lines.append(line)

    rm_line = None
    cp_line = None
    for i, line in enumerate(docs_recipe_lines):
        if "rm -rf" in line and "docs/documentation" in line and "docs/.agents" in line:
            rm_line = i
        if "cp -r documentation" in line and cp_line is None:
            cp_line = i

    assert rm_line is not None, "Makefile 'docs' target must remove old mirrors with 'rm -rf'"
    assert cp_line is not None, "Makefile 'docs' target must copy documentation with 'cp -r'"
    assert rm_line < cp_line, "Makefile 'docs' target must remove mirrors before copying"
