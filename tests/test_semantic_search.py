import os
import sys
import pytest
from unittest.mock import patch, MagicMock

from src.infrastructure.semantic_search import SemanticSearcher, main

@pytest.fixture
def mock_config():
    with patch('src.infrastructure.semantic_search.load_config') as mock_load:
        mock_load.return_value = {"database": {"mode": "sqlite"}}
        yield mock_load

@pytest.fixture
def mock_store_factory():
    with patch('src.infrastructure.vector_store_factory.VectorStoreFactory') as mock_factory:
        mock_store = MagicMock()
        mock_factory.get_store.return_value = mock_store
        yield mock_factory, mock_store

def test_init(mock_config):
    mock_config.return_value = {"database": {"mode": "pgvector"}}
    searcher = SemanticSearcher()
    assert searcher.db_mode == "pgvector"

def test_search_with_results(mock_config, mock_store_factory, capsys):
    mock_factory, mock_store = mock_store_factory
    searcher = SemanticSearcher()
    
    mock_store.query.return_value = [("some content that is somewhat long and interesting to read for vector search purposes", "doc.txt", 0.1234)]
    
    with patch('sentence_transformers.CrossEncoder') as mock_ce:
        mock_ce_instance = MagicMock()
        # Mock predict to return a high score for our single result
        mock_ce_instance.predict.return_value = [0.95]
        mock_ce.return_value = mock_ce_instance
        
        searcher.search("test query", 1)
        
        # Since we expand queries and oversample:
        mock_store.query.assert_called_with("test query", n_results=5)
        captured = capsys.readouterr()
        assert "Re-rank Score:" in captured.out
        assert "Snippet: some content that is somewhat long" in captured.out

def test_search_empty_results(mock_config, mock_store_factory, capsys):
    mock_factory, mock_store = mock_store_factory
    searcher = SemanticSearcher()
    
    mock_store.query.return_value = []
    searcher.search("test query", 1)
        
    captured = capsys.readouterr()
    assert "No relevant results found." in captured.out

@patch('sys.argv', ['semantic_search.py', 'some', 'query'])
@patch.object(SemanticSearcher, 'search')
def test_main(mock_search):
    main()
    mock_search.assert_called_once_with("some query")

@patch('sys.argv', ['semantic_search.py'])
def test_main_no_args(capsys):
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1
    captured = capsys.readouterr()
    assert "Usage: semantic_search.py <query>" in captured.out
