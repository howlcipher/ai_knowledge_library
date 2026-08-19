import os
import sys
import subprocess
import tempfile


def test_pdoc_api_generation():
    """
    Regression test to ensure pdoc can successfully import and generate
    API documentation for all source packages and scripts.
    This prevents hidden ModuleNotFoundError issues caused by missing
    relative sys.path assignments in standalone scripts.
    """
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            [sys.executable, "-m", "pdoc", "./src", "./scripts", "-o", tmpdir],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )

        # If pdoc fails, it usually means a module failed to import when evaluated from the root.
        assert (
            result.returncode == 0
        ), f"API Documentation generation failed!\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"


def test_data_flows_and_control_plane_docs_exist_and_linked():
    """Ensures data_flows.md and CONTROL_PLANE.md exist and are referenced."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_flows = os.path.join(repo_root, "documentation", "data_flows.md")
    control_plane = os.path.join(repo_root, "documentation", "CONTROL_PLANE.md")
    readme = os.path.join(repo_root, "README.md")
    agents_md = os.path.join(repo_root, "AGENTS.md")

    assert os.path.isfile(data_flows), f"{data_flows} does not exist"
    assert os.path.isfile(control_plane), f"{control_plane} does not exist"

    with open(readme, "r", encoding="utf-8") as f:
        readme_text = f.read()
    assert "data_flows.md" in readme_text, "data_flows.md not linked in README.md"

    with open(agents_md, "r", encoding="utf-8") as f:
        agents_text = f.read()
    assert "data_flows.md" in agents_text, "data_flows.md not linked in AGENTS.md"
    assert "CONTROL_PLANE.md" in agents_text, "CONTROL_PLANE.md not linked in AGENTS.md"

