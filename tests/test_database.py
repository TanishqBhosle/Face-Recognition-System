import sqlite3
import pytest
import numpy as np
from modules.resident_manager import ResidentManager

def test_init_db_creates_tables(temp_db):
    """Verify all tables and indexes exist upon initialization."""
    conn = temp_db
    tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    assert "residents" in tables
    assert "entry_logs" in tables
    assert "admins" in tables
    assert "system_config" in tables

def test_register_and_retrieve_resident(resident_mgr, dummy_vector, dummy_image_bytes):
    """Verify resident registration, serialization, and retrieval."""
    res_id = resident_mgr.register_resident(
        full_name="Test Resident",
        flat_number="A-101",
        contact_number="9999999999",
        image_bytes=dummy_image_bytes,
        face_encoding=dummy_vector
    )
    assert res_id > 0
    
    resident = resident_mgr.get_resident_by_id(res_id)
    assert resident is not None
    assert resident.full_name == "Test Resident"
    assert resident.status == "ACTIVE"
    assert resident.face_encoding.shape == (512,)
    assert np.allclose(resident.face_encoding, dummy_vector)

def test_duplicate_resident_detection(resident_mgr, dummy_vector, dummy_image_bytes):
    """System must detect near-duplicate facial embeddings."""
    resident_mgr.register_resident(
        full_name="Original Resident",
        flat_number="B-202",
        contact_number=None,
        image_bytes=dummy_image_bytes,
        face_encoding=dummy_vector
    )
    
    # Check duplicate with the exact same vector
    duplicate = resident_mgr.check_duplicate(dummy_vector, threshold=0.35)
    assert duplicate is not None
    assert duplicate.full_name == "Original Resident"

def test_deactivate_resident(resident_mgr, dummy_vector, dummy_image_bytes):
    """Deactivated resident must be excluded from get_all_active_residents()."""
    res_id = resident_mgr.register_resident("Deactivate Me", "C-303", None, dummy_image_bytes, dummy_vector)
    resident_mgr.set_status(res_id, "INACTIVE")
    
    active_ids = [r.resident_id for r in resident_mgr.get_all_active_residents()]
    assert res_id not in active_ids

def test_update_resident_metadata(resident_mgr, dummy_vector, dummy_image_bytes):
    """Verify editing resident details."""
    res_id = resident_mgr.register_resident("Old Name", "D-401", "111", dummy_image_bytes, dummy_vector)
    success = resident_mgr.update_resident(res_id, "New Name", "D-402", "222")
    assert success is True
    
    updated = resident_mgr.get_resident_by_id(res_id)
    assert updated.full_name == "New Name"
    assert updated.flat_number == "D-402"
    assert updated.contact_number == "222"
