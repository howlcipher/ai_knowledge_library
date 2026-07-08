import pytest
from unittest.mock import patch, MagicMock
import sys

# Mock streamlit before importing KnowledgeUI
sys.modules['streamlit'] = MagicMock()
sys.modules['chromadb'] = MagicMock()

from src.ui.web_ui import KnowledgeUI, main

@pytest.fixture
def mock_streamlit():
    with patch('src.ui.web_ui.st') as mock_st:
        yield mock_st

@pytest.fixture
def mock_store_factory():
    with patch('src.infrastructure.vector_store_factory.VectorStoreFactory') as mock_factory:
        mock_store = MagicMock()
        mock_factory.get_store.return_value = mock_store
        yield mock_factory, mock_store

def test_knowledge_ui_init(mock_streamlit, mock_store_factory):
    mock_factory, mock_store = mock_store_factory
    ui = KnowledgeUI()
    assert ui.store == mock_store

def test_knowledge_ui_render(mock_streamlit, mock_store_factory):
    ui = KnowledgeUI()
    mock_streamlit.text_input.return_value = "query"
    mock_streamlit.button.return_value = True
    
    tab_mock1 = MagicMock()
    tab_mock2 = MagicMock()
    tab_mock1.__enter__ = MagicMock(return_value=tab_mock1)
    tab_mock1.__exit__ = MagicMock(return_value=None)
    tab_mock2.__enter__ = MagicMock(return_value=tab_mock2)
    tab_mock2.__exit__ = MagicMock(return_value=None)
    mock_streamlit.tabs.return_value = (tab_mock1, tab_mock2)
    
    with patch.object(ui, '_handle_search') as mock_search:
        ui.render()
        mock_search.assert_called_with("query")

def test_knowledge_ui_handle_search_no_results(mock_streamlit, mock_store_factory):
    mock_factory, mock_store = mock_store_factory
    ui = KnowledgeUI()
    mock_store.query.return_value = []
    
    ui._handle_search("test")
    mock_streamlit.warning.assert_called_with("No relevant results found.")

def test_knowledge_ui_handle_search_with_results(mock_streamlit, mock_store_factory):
    mock_factory, mock_store = mock_store_factory
    ui = KnowledgeUI()
    
    mock_store.query.return_value = [("doc1", "src1", 0.1), ("doc2", "", 0.2)]
    
    with patch.object(ui, '_display_results') as mock_display:
        ui._handle_search("test")
        mock_streamlit.success.assert_called_with("Found relevant context!")
        mock_display.assert_called_with([("doc1", "src1", 0.1), ("doc2", "", 0.2)])

def test_knowledge_ui_display_results(mock_streamlit, mock_store_factory):
    ui = KnowledgeUI()
    results = [("doc1", "src1", 0.1)]
    ui._display_results(results)
    mock_streamlit.expander.assert_called_with("Result 1 | Source: src1 (Confidence: 0.90)")
    mock_streamlit.write.assert_called_with("doc1")

def test_main(mock_streamlit, mock_store_factory):
    with patch('src.ui.web_ui.KnowledgeUI') as mock_ui_class:
        mock_ui = MagicMock()
        mock_ui_class.return_value = mock_ui
        main()
        mock_ui_class.assert_called_once()
        mock_ui.render.assert_called_once()
