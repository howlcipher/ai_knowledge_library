"""Tests for the changed-code test selector (scripts/select_relevant_tests.py)."""

from scripts.select_relevant_tests import module_names, select_tests

TEST_SOURCES = {
    "tests/test_provider_preflight.py": "from src.core.provider_preflight import run_preflight",
    "tests/test_config.py": "import yaml\nfrom src.core import config",
    "tests/test_tools.py": "def test_helpers():\n    pass",
}


def test_module_names_src_layout():
    names = module_names("src/core/provider_preflight.py")
    assert "provider_preflight" in names
    assert "src.core.provider_preflight" in names
    assert "core.provider_preflight" in names


def test_module_names_package_init_uses_package():
    names = module_names("src/core/__init__.py")
    assert "core" in names
    assert "__init__" not in names


def test_changed_source_selects_referencing_tests():
    selected, uncovered, trigger = select_tests(
        ["src/core/provider_preflight.py"], TEST_SOURCES
    )
    assert selected == ["tests/test_provider_preflight.py"]
    assert uncovered == []
    assert trigger is None


def test_changed_test_file_selects_itself():
    selected, uncovered, trigger = select_tests(
        ["tests/test_config.py"], TEST_SOURCES
    )
    assert selected == ["tests/test_config.py"]
    assert trigger is None


def test_unreferenced_source_is_reported_uncovered():
    selected, uncovered, trigger = select_tests(
        ["src/core/brand_new_module.py"], TEST_SOURCES
    )
    assert selected == []
    assert uncovered == ["src/core/brand_new_module.py"]
    assert trigger is None


def test_broad_surface_change_triggers_full_suite():
    for path in ("Makefile", "pyproject.toml", "config/settings.yaml", "cmd/installer/main.go"):
        _, _, trigger = select_tests([path], TEST_SOURCES)
        assert trigger == path, path


def test_docs_only_change_selects_nothing():
    selected, uncovered, trigger = select_tests(
        ["documentation/some_doc.md", "README.md"], TEST_SOURCES
    )
    assert selected == []
    assert uncovered == []
    assert trigger is None


def test_full_suite_trigger_prefix_must_be_directory():
    # "configure.py" must not match the "config/" directory trigger.
    selected, uncovered, trigger = select_tests(["configure.py"], TEST_SOURCES)
    assert trigger is None
    assert uncovered == ["configure.py"]
