import pytest
from unittest.mock import patch, MagicMock
import os
import sys

# Mock streamlit and chromadb before importing KnowledgeUI
sys.modules['streamlit'] = MagicMock()
sys.modules['chromadb'] = MagicMock()

from src.ui.web_ui import KnowledgeUI, main

@pytest.fixture
def mock_streamlit():
    with patch('src.ui.web_ui.st') as mock_st:
        yield mock_st

@pytest.fixture
def mock_chromadb():
    with patch('src.ui.web_ui.chromadb') as mock_chroma:
        yield mock_chroma

def test_knowledge_ui_init_no_db(mock_streamlit, mock_chromadb):
    with patch('os.path.exists', return_value=False), patch('config.loader.get_chroma_db_path', return_value='/fake/path'):
        KnowledgeUI()
        mock_streamlit.error.assert_called_once()
        mock_streamlit.stop.assert_called_once()

def test_knowledge_ui_init_success(mock_streamlit, mock_chromadb):
    mock_client = MagicMock()
    mock_chromadb.PersistentClient.return_value = mock_client
    
    with patch('os.path.exists', return_value=True), \
         patch('config.loader.get_chroma_db_path', return_value='/fake/path'):
        ui = KnowledgeUI()
        
        assert ui.client == mock_client
        mock_client.get_collection.assert_called_with(name="ai_library_knowledge")
        assert ui.collection == mock_client.get_collection.return_value

def test_knowledge_ui_init_collection_not_found(mock_streamlit, mock_chromadb):
    mock_client = MagicMock()
    mock_client.get_collection.side_effect = Exception("Not found")
    mock_chromadb.PersistentClient.return_value = mock_client
    
    with patch('os.path.exists', return_value=True), \
         patch('config.loader.get_chroma_db_path', return_value='/fake/path'):
        KnowledgeUI()
        mock_streamlit.error.assert_called_with("Collection not found. Please rebuild the index.")
        mock_streamlit.stop.assert_called()

def test_knowledge_ui_render(mock_streamlit, mock_chromadb):
    mock_client = MagicMock()
    mock_chromadb.PersistentClient.return_value = mock_client
    
    with patch('os.path.exists', return_value=True), \
         patch('config.loader.get_chroma_db_path', return_value='/fake/path'):
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

def test_knowledge_ui_handle_search_no_results(mock_streamlit, mock_chromadb):
    mock_client = MagicMock()
    mock_chromadb.PersistentClient.return_value = mock_client
    
    with patch('os.path.exists', return_value=True), \
         patch('config.loader.get_chroma_db_path', return_value='/fake/path'):
        ui = KnowledgeUI()
        
        ui.collection.query.return_value = {}
        
        ui._handle_search("test")
        mock_streamlit.warning.assert_called_with("No relevant results found.")

def test_knowledge_ui_handle_search_with_results(mock_streamlit, mock_chromadb):
    mock_client = MagicMock()
    mock_chromadb.PersistentClient.return_value = mock_client
    
    with patch('os.path.exists', return_value=True), \
         patch('config.loader.get_chroma_db_path', return_value='/fake/path'):
        ui = KnowledgeUI()
        
        ui.collection.query.return_value = {
            "documents": [["doc1", "doc2"]],
            "metadatas": [[{"source": "src1"}, {}]],
            "distances": [[0.1, 0.2]]
        }
        
        with patch.object(ui, '_display_results') as mock_display:
            ui._handle_search("test")
            mock_streamlit.success.assert_called_with("Found relevant context!")
            mock_display.assert_called_with(["doc1", "doc2"], [{"source": "src1"}, {}], [0.1, 0.2])

def test_knowledge_ui_display_results(mock_streamlit, mock_chromadb):
    mock_client = MagicMock()
    mock_chromadb.PersistentClient.return_value = mock_client
    
    with patch('os.path.exists', return_value=True), \
         patch('config.loader.get_chroma_db_path', return_value='/fake/path'):
        ui = KnowledgeUI()
        
        documents = ["doc1"]
        metadatas = [{"source": "src1"}]
        distances = [0.1]
        
        ui._display_results(documents, metadatas, distances)
        mock_streamlit.expander.assert_called_with("Result 1 | Source: src1 (Confidence: 0.90)")
        mock_streamlit.write.assert_called_with("doc1")

def test_main(mock_streamlit, mock_chromadb):
    with patch('src.ui.web_ui.KnowledgeUI') as mock_ui_class:
        mock_ui = MagicMock()
        mock_ui_class.return_value = mock_ui
        
        main()
        
        mock_ui_class.assert_called_once()
        mock_ui.render.assert_called_once()
