import pytest
from unittest.mock import MagicMock, patch

@patch('chromadb.PersistentClient')
def test_chroma_db_mock(mock_client):
    # Setup mock
    mock_collection = MagicMock()
    mock_client.return_value.get_or_create_collection.return_value = mock_collection
    
    # Simulate adding documents
    mock_collection.add(
        documents=["test doc"],
        metadatas=[{"source": "test"}],
        ids=["id1"]
    )
    
    # Verify mock was called correctly
    mock_collection.add.assert_called_once_with(
        documents=["test doc"],
        metadatas=[{"source": "test"}],
        ids=["id1"]
    )
    assert mock_client.called
