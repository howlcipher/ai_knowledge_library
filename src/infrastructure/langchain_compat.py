"""
langchain_compat.py
Isolates the Pydantic V1 compatibility warning emitted by langchain-core under Python 3.14.
Importing this module suppresses the warning during the initial load of langchain_core.utils.pydantic.
"""
import warnings

try:
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater.",
            category=UserWarning,
            module="langchain_core.utils.pydantic"
        )
        import langchain_core.utils.pydantic  # noqa: F401
except ImportError:
    pass
