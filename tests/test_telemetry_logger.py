import pytest
import os
import sqlite3
import pandas as pd
from datetime import datetime
from unittest.mock import patch, MagicMock

import src.infrastructure.telemetry_logger as telemetry_logger

@pytest.fixture
def mock_db_path(tmp_path, monkeypatch):
    db_file = tmp_path / "telemetry.db"
    
    # Mock get_telemetry_db_path directly instead of os.path.expanduser
    def mock_get_path():
        return str(db_file)
        
    monkeypatch.setattr(telemetry_logger, "get_telemetry_db_path", mock_get_path)
    return str(db_file)

def test_init_db(mock_db_path):
    telemetry_logger.init_db()
    assert os.path.exists(mock_db_path)
    
    # Verify table schema
    conn = sqlite3.connect(mock_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='api_telemetry'")
    assert cursor.fetchone() is not None
    conn.close()

def test_log_telemetry(mock_db_path):
    telemetry_logger.log_telemetry("test-model", 10, 20, 30, 0.05, 1.2)
    
    conn = sqlite3.connect(mock_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT model, prompt_tokens, completion_tokens, total_tokens, cost, latency_seconds, cached_tokens FROM api_telemetry")
    row = cursor.fetchone()
    
    assert row is not None
    assert row[0] == "test-model"
    assert row[1] == 10
    assert row[2] == 20
    assert row[3] == 30
    assert row[4] == 0.05
    assert row[5] == 1.2
    assert row[6] == 0
    conn.close()

def test_get_telemetry_data_with_pandas(mock_db_path):
    telemetry_logger.log_telemetry("test-model", 10, 20, 30, 0.05, 1.2)
    df = telemetry_logger.get_telemetry_data()
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df) == 1
    assert df.iloc[0]["model"] == "test-model"

def test_get_telemetry_data_without_pandas(mock_db_path, monkeypatch):
    telemetry_logger.log_telemetry("test-model", 10, 20, 30, 0.05, 1.2)
    
    # Mock ImportError for pandas
    import builtins
    real_import = builtins.__import__
    def mock_import(name, *args, **kwargs):
        if name == 'pandas':
            raise ImportError("No module named pandas")
        return real_import(name, *args, **kwargs)
        
    monkeypatch.setattr(builtins, "__import__", mock_import)
    
    data = telemetry_logger.get_telemetry_data()
    
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["model"] == "test-model"
    assert data[0]["prompt_tokens"] == 10

def test_main(mock_db_path, capsys):
    telemetry_logger.log_telemetry("test-main", 5, 5, 10, 0.01, 0.5)
    telemetry_logger.main()
    captured = capsys.readouterr()
    assert "Telemetry Data:" in captured.out
    assert "test-main" in captured.out
