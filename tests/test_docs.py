import os
import sys
import subprocess
import tempfile


def test_pdoc_api_generation():
    """
    Regression test to ensure pdoc can successfully import and generate
    API documentation for all tools and scripts.
    This prevents hidden ModuleNotFoundError issues caused by missing
    relative sys.path assignments in standalone scripts.
    """
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            [sys.executable, "-m", "pdoc", "./tools", "./scripts", "-o", tmpdir],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )

        # If pdoc fails, it usually means a module failed to import when evaluated from the root.
        assert (
            result.returncode == 0
        ), f"API Documentation generation failed!\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
