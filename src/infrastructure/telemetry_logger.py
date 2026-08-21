#!/usr/bin/env python3
"""
Telemetry Logger for tracking LLM token consumption, cost, and latency.
Stores data in a SQLite database.
"""

import os
import sqlite3
from datetime import datetime
from typing import Any, Optional


def get_telemetry_db_path() -> str:
    """Returns the path to the telemetry SQLite database."""
    from src.infrastructure.config_loader import default_loader

    # Store in repo root's .telemetry dir by default
    data_dir = os.path.join(default_loader.get_repo_root(), ".telemetry")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)

    return os.path.join(data_dir, "telemetry.db")


def init_db():
    """Initializes the SQLite database table if it doesn't exist."""
    db_path = get_telemetry_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            model TEXT NOT NULL,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            total_tokens INTEGER,
            cost REAL,
            latency_seconds REAL,
            cached_tokens INTEGER DEFAULT 0
        )
    """)

    # Attempt to migrate existing database to add cached_tokens column
    try:
        cursor.execute(
            "ALTER TABLE api_telemetry ADD COLUMN cached_tokens INTEGER DEFAULT 0"
        )
    except sqlite3.OperationalError:
        pass  # Column likely already exists

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gate_failures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            model TEXT NOT NULL,
            pass_number INTEGER,
            attempt INTEGER,
            stage TEXT,
            error_message TEXT
        )
    """)

    conn.commit()
    conn.close()


def log_telemetry(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    cost: float,
    latency: float,
    cached_tokens: int = 0,
):
    """
    Logs an API call to the telemetry database.
    """
    init_db()
    db_path = get_telemetry_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    timestamp = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO api_telemetry (timestamp, model, prompt_tokens, completion_tokens, total_tokens, cost, latency_seconds, cached_tokens)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            timestamp,
            model,
            prompt_tokens,
            completion_tokens,
            total_tokens,
            cost,
            latency,
            cached_tokens,
        ),
    )

    conn.commit()
    conn.close()


def extract_cached_tokens(usage: Any) -> int:
    """Extracts cached tokens count from API usage object."""
    if not usage:
        return 0
    cached = getattr(usage, "cache_read_input_tokens", 0)
    if not isinstance(cached, (int, float)):
        cached = 0
    if not cached and hasattr(usage, "prompt_tokens_details"):
        details = getattr(usage, "prompt_tokens_details", {})
        if isinstance(details, dict):
            cached = details.get("cached_tokens", 0)
        elif hasattr(details, "cached_tokens"):
            cached = getattr(details, "cached_tokens", 0)
    if not isinstance(cached, (int, float)):
        cached = 0
    return int(cached)


def log_response_telemetry(response: Any, cost: float, latency: float, model: Optional[str] = None) -> None:
    """Convenience helper to record telemetry directly from an LLM response object."""
    usage = getattr(response, "usage", None)
    cached = extract_cached_tokens(usage)
    eff_model = str(model or getattr(response, "model", "unknown"))
    pt = getattr(usage, "prompt_tokens", 0) if usage else 0
    ct = getattr(usage, "completion_tokens", 0) if usage else 0
    tt = getattr(usage, "total_tokens", 0) if usage else 0

    log_telemetry(
        model=eff_model,
        prompt_tokens=int(pt) if isinstance(pt, (int, float)) else 0,
        completion_tokens=int(ct) if isinstance(ct, (int, float)) else 0,
        total_tokens=int(tt) if isinstance(tt, (int, float)) else 0,
        cost=float(cost) if isinstance(cost, (int, float)) else 0.0,
        latency=float(latency) if isinstance(latency, (int, float)) else 0.0,
        cached_tokens=cached,
    )


def log_gate_failure(
    model: str,
    pass_number: int,
    attempt: int,
    stage: str,
    error_message: str,
):
    """
    Logs a validation gate failed attempt to the telemetry database.
    """
    init_db()
    db_path = get_telemetry_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    timestamp = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO gate_failures (timestamp, model, pass_number, attempt, stage, error_message)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (timestamp, model, pass_number, attempt, stage, error_message),
    )

    conn.commit()
    conn.close()


def get_gate_failure_data():
    """
    Retrieves all gate failure data. Returns a pandas DataFrame if pandas is
    installed, otherwise returns a list of dictionaries.
    """
    init_db()
    db_path = get_telemetry_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT timestamp, model, pass_number, attempt, stage, error_message FROM gate_failures"
    )
    rows = cursor.fetchall()
    columns = ["timestamp", "model", "pass_number", "attempt", "stage", "error_message"]
    conn.close()
    return _format_query_results(rows, columns)


def _format_query_results(rows: list, columns: list):
    try:
        import pandas as pd

        df = pd.DataFrame(rows, columns=columns)
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    except ImportError:
        return [dict(zip(columns, row)) for row in rows]


def get_telemetry_data():
    """
    Retrieves all telemetry data. Returns a pandas DataFrame if pandas is installed,
    otherwise returns a list of dictionaries.
    """
    init_db()
    db_path = get_telemetry_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT timestamp, model, prompt_tokens, completion_tokens, total_tokens, cost, latency_seconds, cached_tokens FROM api_telemetry"
    )
    rows = cursor.fetchall()
    columns = [
        "timestamp",
        "model",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "cost",
        "latency_seconds",
        "cached_tokens",
    ]
    conn.close()
    return _format_query_results(rows, columns)


def main():
    """CLI entrypoint for viewing telemetry data."""
    data = get_telemetry_data()
    print("Telemetry Data:")
    print(data)


if __name__ == "__main__":
    main()
