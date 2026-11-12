import sys
import io
from pathlib import Path
from PIL import Image

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pytest
import sqlite3
import numpy as np
from database.db import init_db, get_connection
from modules.resident_manager import ResidentManager
from modules.access_controller import AccessController
from modules.entry_logger import EntryLogger

@pytest.fixture
def temp_db(tmp_path):
    """Provides an isolated SQLite test database."""
    db_file = tmp_path / "test_security.db"
    schema_file = BASE_DIR / "database" / "schema.sql"
    init_db(db_path=str(db_file), schema_path=str(schema_file))
    conn = get_connection(db_path=str(db_file))
    yield conn
    conn.close()

@pytest.fixture
def dummy_vector():
    """Generates a normalized 512-dimensional vector."""
    np.random.seed(123)
    vec = np.random.randn(512).astype(np.float32)
    return vec / np.linalg.norm(vec)

@pytest.fixture
def dummy_image_bytes():
    """Generates a valid 100x100 JPEG image as bytes."""
    img = Image.new("RGB", (100, 100), color=(41, 128, 185))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

@pytest.fixture
def mock_face_image():
    """Generates a synthetic 128x128x3 uint8 image."""
    return np.random.randint(0, 256, (128, 128, 3), dtype=np.uint8)

@pytest.fixture
def resident_mgr(tmp_path, monkeypatch):
    """Provides a ResidentManager pointing to a temporary test directory."""
    db_file = tmp_path / "test_residents.db"
    schema_file = BASE_DIR / "database" / "schema.sql"
    init_db(db_path=str(db_file), schema_path=str(schema_file))
    
    # Patch DB_PATH and RESIDENTS_DIR
    test_residents_dir = tmp_path / "residents"
    test_residents_dir.mkdir(parents=True, exist_ok=True)
    
    monkeypatch.setattr("modules.resident_manager.get_connection", lambda: get_connection(str(db_file)))
    monkeypatch.setattr("modules.resident_manager.RESIDENTS_DIR", test_residents_dir)
    monkeypatch.setattr("modules.resident_manager.get_db_cursor", lambda: get_connection(str(db_file)))
    
    # ResidentManager instance with isolated db_path
    mgr = ResidentManager()
    return mgr
