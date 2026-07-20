import os
import sys
from unittest.mock import MagicMock

# Ensure the src directory is on sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import src.infrastructure.pgvector_backend as pg_mod


def _make_store(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    monkeypatch.setattr(pg_mod.psycopg2, "connect", lambda dsn: mock_conn)
    monkeypatch.setattr(pg_mod, "register_vector", lambda conn: None)
    mock_model = MagicMock()
    monkeypatch.setattr(pg_mod, "SentenceTransformer", lambda name: mock_model)
    store = pg_mod.PgVectorStore()
    return store, mock_conn, mock_cursor, mock_model


def test_init_db_creates_chunk_id_unique_index(monkeypatch):
    store, mock_conn, mock_cursor, _ = _make_store(monkeypatch)
    store.init_db()
    executed_sql = " ".join(str(call.args[0]) for call in mock_cursor.execute.call_args_list)
    assert "chunk_id" in executed_sql
    assert "UNIQUE" in executed_sql.upper()


def test_upsert_uses_on_conflict_with_provided_ids(monkeypatch):
    store, mock_conn, mock_cursor, mock_model = _make_store(monkeypatch)
    mock_model.encode.return_value = [MagicMock(tolist=lambda: [0.1, 0.2])]
    store.upsert(docs=["hello"], metadatas=[{"source": "a.md", "chunk": 2}], ids=["a.md_2"])
    args, kwargs = mock_cursor.execute.call_args
    sql, params = args[0], args[1]
    assert "ON CONFLICT" in sql.upper()
    assert params[0] == "a.md_2"
    assert params[1] == "hello"
    assert params[2] == "a.md"
    assert params[3] == 2


def test_upsert_calling_twice_with_same_id_issues_two_on_conflict_statements(monkeypatch):
    store, mock_conn, mock_cursor, mock_model = _make_store(monkeypatch)
    mock_model.encode.return_value = [MagicMock(tolist=lambda: [0.1, 0.2])]
    store.upsert(docs=["v1"], metadatas=[{"source": "a.md", "chunk": 0}], ids=["a.md_0"])
    store.upsert(docs=["v2"], metadatas=[{"source": "a.md", "chunk": 0}], ids=["a.md_0"])
    assert mock_cursor.execute.call_count == 2
    for call in mock_cursor.execute.call_args_list:
        assert "ON CONFLICT" in call.args[0].upper()


def test_upsert_defaults_ids_when_not_provided(monkeypatch):
    store, mock_conn, mock_cursor, mock_model = _make_store(monkeypatch)
    mock_model.encode.return_value = [MagicMock(tolist=lambda: [0.1]), MagicMock(tolist=lambda: [0.2])]
    store.upsert(docs=["d1", "d2"], metadatas=[{"source": "x"}, {"source": "y"}], ids=None)
    calls = mock_cursor.execute.call_args_list
    assert calls[0].args[1][0] == "doc_0"
    assert calls[1].args[1][0] == "doc_1"
