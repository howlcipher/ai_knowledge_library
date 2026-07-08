import os
import sys
import pytest
from unittest.mock import patch, MagicMock, mock_open

# Ensure tools can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.semantic_search import SemanticSearcher, main

@pytest.fixture
def mock_config():
    with patch('src.infrastructure.semantic_search.load_config') as mock_load:
        mock_load.return_value = {"database": {"mode": "sqlite"}}
        yield mock_load

@pytest.fixture
def searcher(mock_config):
    return SemanticSearcher()

def test_init(mock_config):
    mock_config.return_value = {"database": {"mode": "pgvector"}}
    searcher = SemanticSearcher()
    assert searcher.db_mode == "pgvector"

@patch.object(SemanticSearcher, '_search_pgvector')
@patch.object(SemanticSearcher, '_search_chromadb')
def test_search_routing_pgvector(mock_chroma, mock_pg, mock_config):
    mock_config.return_value = {"database": {"mode": "pgvector"}}
    searcher = SemanticSearcher()
    searcher.search("test query", 5)
    mock_pg.assert_called_once_with("test query", 5)
    mock_chroma.assert_not_called()

@patch.object(SemanticSearcher, '_search_pgvector')
@patch.object(SemanticSearcher, '_search_chromadb')
def test_search_routing_chromadb(mock_chroma, mock_pg, mock_config):
    mock_config.return_value = {"database": {"mode": "sqlite"}}
    searcher = SemanticSearcher()
    searcher.search("test query", 3)
    mock_chroma.assert_called_once_with("test query", 3)
    mock_pg.assert_not_called()

@patch('src.infrastructure.semantic_search.PgVectorStore', create=True)
def test_search_pgvector_with_results(mock_pgstore_class, searcher, capsys):
    mock_store = MagicMock()
    mock_pgstore_class.return_value = mock_store
    mock_store.query.return_value = [("some content that is somewhat long and interesting to read for vector search purposes", "doc.txt", 0.1234)]
    
    # We have to patch it inside sys.modules because it's imported locally
    with patch.dict('sys.modules', {'src.infrastructure.pgvector_backend': MagicMock(PgVectorStore=mock_pgstore_class)}):
        searcher._search_pgvector("test query", 1)
        
    mock_store.query.assert_called_once_with("test query", n_results=1)
    captured = capsys.readouterr()
    assert "[1] Source: doc.txt (Distance: 0.1234)" in captured.out
    assert "Snippet: some content that is somewhat long" in captured.out

@patch('src.infrastructure.semantic_search.PgVectorStore', create=True)
def test_search_pgvector_empty_results(mock_pgstore_class, searcher, capsys):
    mock_store = MagicMock()
    mock_pgstore_class.return_value = mock_store
    mock_store.query.return_value = []
    
    with patch.dict('sys.modules', {'src.infrastructure.pgvector_backend': MagicMock(PgVectorStore=mock_pgstore_class)}):
        searcher._search_pgvector("test query", 1)
        
    captured = capsys.readouterr()
    assert "No relevant results found." in captured.out

@patch('src.infrastructure.semantic_search.get_chroma_db_path')
@patch('os.path.exists')
def test_search_chromadb_with_results(mock_exists, mock_get_path, searcher, capsys):
    mock_get_path.return_value = "/fake/db/path"
    mock_exists.return_value = True
    
    mock_chromadb = MagicMock()
    mock_client = MagicMock()
    mock_chromadb.PersistentClient.return_value = mock_client
    mock_collection = MagicMock()
    mock_client.get_collection.return_value = mock_collection
    
    mock_collection.query.return_value = {
        "documents": [["this is a document text for chromadb search testing"]],
        "metadatas": [[{"source": "fake_source.md"}]],
        "distances": [[0.5678]]
    }
    
    with patch.dict('sys.modules', {'chromadb': mock_chromadb}):
        searcher._search_chromadb("test query", 1)
        
    captured = capsys.readouterr()
    assert "[1] Source: fake_source.md (Distance: 0.5678)" in captured.out
    assert "Snippet: this is a document text" in captured.out

@patch('src.infrastructure.semantic_search.get_chroma_db_path')
@patch('os.path.exists')
def test_search_chromadb_empty_results(mock_exists, mock_get_path, searcher, capsys):
    mock_get_path.return_value = "/fake/db/path"
    mock_exists.return_value = True
    
    mock_chromadb = MagicMock()
    mock_client = MagicMock()
    mock_chromadb.PersistentClient.return_value = mock_client
    mock_collection = MagicMock()
    mock_client.get_collection.return_value = mock_collection
    
    mock_collection.query.return_value = {
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]]
    }
    
    with patch.dict('sys.modules', {'chromadb': mock_chromadb}):
        searcher._search_chromadb("test query", 1)
        
    captured = capsys.readouterr()
    assert "No relevant results found." in captured.out

@patch('src.infrastructure.semantic_search.get_chroma_db_path')
@patch('os.path.exists')
def test_search_chromadb_no_db(mock_exists, mock_get_path, searcher, capsys):
    mock_get_path.return_value = "/fake/db/path"
    mock_exists.return_value = False
    
    mock_chromadb = MagicMock()
    
    with patch.dict('sys.modules', {'chromadb': mock_chromadb}):
        with pytest.raises(SystemExit) as e:
            searcher._search_chromadb("test query", 1)
        assert e.value.code == 1
        
    captured = capsys.readouterr()
    assert "Vector database not found." in captured.out

@patch('src.infrastructure.semantic_search.get_chroma_db_path')
@patch('os.path.exists')
def test_search_chromadb_no_collection(mock_exists, mock_get_path, searcher, capsys):
    mock_get_path.return_value = "/fake/db/path"
    mock_exists.return_value = True
    
    mock_chromadb = MagicMock()
    mock_client = MagicMock()
    mock_chromadb.PersistentClient.return_value = mock_client
    mock_client.get_collection.side_effect = Exception("Collection not found")
    
    with patch.dict('sys.modules', {'chromadb': mock_chromadb}):
        with pytest.raises(SystemExit) as e:
            searcher._search_chromadb("test query", 1)
        assert e.value.code == 1
        
    captured = capsys.readouterr()
    assert "Collection not found." in captured.out

def test_search_chromadb_import_error(searcher, capsys):
    # Test when chromadb is not installed
    with patch.dict('sys.modules', {'chromadb': None}):
        with pytest.raises(SystemExit) as e:
            searcher._search_chromadb("test query", 1)
        assert e.value.code == 1
        
    captured = capsys.readouterr()
    assert "Error: chromadb not installed." in captured.out

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
