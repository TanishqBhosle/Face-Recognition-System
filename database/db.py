import sqlite3
from contextlib import contextmanager
from typing import Generator
from config.settings import DB_PATH, SCHEMA_PATH

def get_connection(db_path: str = str(DB_PATH)) -> sqlite3.Connection:
    """
    Returns a thread-safe connection to the SQLite database with row_factory enabled
    and foreign keys turned on.
    """
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path: str = str(DB_PATH), schema_path: str = str(SCHEMA_PATH)) -> None:
    """
    Runs schema.sql against the database file. Idempotent.
    """
    conn = get_connection(db_path)
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            ddl = f.read()
        conn.executescript(ddl)
        conn.commit()
    finally:
        conn.close()

@contextmanager
def get_db_cursor(db_path: str = str(DB_PATH)) -> Generator[sqlite3.Cursor, None, None]:
    """
    Context manager providing a cursor with automatic commit and rollback.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

