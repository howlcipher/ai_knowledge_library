import os
import sys
import pytest
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_tools_have_main_function():
    tools_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tools'))
    tool_files = [f for f in os.listdir(tools_dir) if f.endswith('.py') and f != '__init__.py']
    
    assert len(tool_files) > 0, "No tools found in the tools directory."
    
    for tool_file in tool_files:
        path = os.path.join(tools_dir, tool_file)
        # We wrap in try-except to avoid tests failing purely due to missing pip packages 
        # in minimal test environments, but we still ensure the file is syntactically valid
        try:
            mod = load_module(tool_file[:-3], path)
            assert hasattr(mod, 'main'), f"{tool_file} is missing a main() entrypoint."
        except (ImportError, SystemExit):
            pass # Skip if dependency is missing during minimal testing

