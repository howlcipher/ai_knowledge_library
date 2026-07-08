import pytest
import yaml
import os
import sys

# Add tools to sys.path to resolve internal imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))

from tools.tui import AILibraryTUI, ChatArea
from textual.widgets import Select, Input, Label

@pytest.fixture
def mock_config(tmp_path, monkeypatch):
    config_file = tmp_path / "settings.yaml"
    
    class MockConfigLoader:
        def __init__(self):
            self.config_path = str(config_file)
            self.data = {"llm_model": "gemini/gemini-1.5-pro"}
            
        def get(self, key, default):
            return self.data.get(key, default)
            
    monkeypatch.setattr("tools.tui.ConfigLoader", MockConfigLoader)
    return str(config_file)

@pytest.mark.asyncio
async def test_tui_initialization(mock_config):
    app = AILibraryTUI()
    async with app.run_test() as pilot:
        assert app.title == "AILibraryTUI"

@pytest.mark.asyncio
async def test_tui_select_changed(mock_config):
    app = AILibraryTUI()
    async with app.run_test() as pilot:
        select = app.query_one("#llm-select", Select)
        
        select.value = "openai/gpt-4o"
        await pilot.pause()
        
        assert app.current_model == "openai/gpt-4o"
        
        if os.path.exists(mock_config):
            with open(mock_config, "r") as f:
                data = yaml.safe_load(f)
                assert data["llm_model"] == "openai/gpt-4o"

@pytest.mark.asyncio
async def test_tui_input_submitted(mock_config):
    app = AILibraryTUI()
    async with app.run_test() as pilot:
        input_box = app.query_one("#input-box", Input)
        
        input_box.value = "   "
        await input_box.action_submit()
        await pilot.pause()
        
        input_box.value = "Hello AI"
        await input_box.action_submit()
        await pilot.pause()
        
        container = app.query_one("#chat-container")
        assert len(container.children) >= 2

@pytest.mark.asyncio
async def test_tui_action_clear_chat(mock_config):
    app = AILibraryTUI()
    async with app.run_test() as pilot:
        input_box = app.query_one("#input-box", Input)
        input_box.value = "Hello"
        await input_box.action_submit()
        await pilot.pause()
        
        app.action_clear_chat()
        await pilot.pause()
        
        container = app.query_one("#chat-container")
        assert len(container.children) == 0

def test_tui_main(monkeypatch):
    import tools.tui
    
    class MockApp:
        def run(self):
            self.ran = True
            
    def mock_tui():
        return MockApp()
        
    monkeypatch.setattr(tools.tui, "AILibraryTUI", mock_tui)
    tools.tui.main()
