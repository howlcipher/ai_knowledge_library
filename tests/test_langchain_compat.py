import subprocess
import sys

def test_langchain_pydantic_warning_is_isolated():
    """
    Ensures that importing our core modules doesn't emit the langchain Pydantic V1 compatibility warning.
    This protects against regressions where langchain is imported without the compat isolation in Python 3.14.
    """
    code = (
        "import warnings\n"
        "warnings.simplefilter('error', UserWarning)\n"
        "import src.core.orchestrator\n"
        "import src.core.web_research\n"
        "print('clean')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], 
        capture_output=True, 
        text=True,
        env={"PYTHONPATH": "."}
    )
    assert result.returncode == 0, f"Importing core modules emitted a warning or error:\n{result.stderr}"
    assert "clean" in result.stdout
