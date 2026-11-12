# Comprehensive Testing Strategy & Test Suite Specification
# Smart Society Security System

---

## 1. Testing Strategy Overview

The testing framework guarantees that all subsystems—from low-level computer vision capture and deep learning embedding extraction to database persistence and Streamlit business logic—operate deterministically, securely, and with zero unhandled exceptions.

```
┌─────────────────────────────────────────────────────────────┐
│                 End-to-End Pipeline Tests                  │
│       (Camera Frame -> Detection -> Decision -> DB Log)      │
├─────────────────────────────────────────────────────────────┤
│                  Integration Test Suite                     │
│    (Database CRUD + Embedding Engine + Controller Rules)    │
├─────────────────────────────────────────────────────────────┤
│                     Unit Test Suite                         │
│  (test_recognition, test_database, test_access, test_report)│
└─────────────────────────────────────────────────────────────┘
```

- **Framework**: `pytest 8.x`
- **Mocking & Isolation**: `unittest.mock` / `pytest-mock`
- **Coverage Tool**: `pytest-cov` (target $\ge 85\%$ module coverage)
- **Synthetic Test Data**: Mock 512-dimensional normalized float32 vectors generated via `np.random` to enable fast CI runs without loading full neural weights during unit testing.

---

## 2. Test Suite Organization

```
tests/
├── conftest.py                   # Shared pytest fixtures (mock DB, dummy embeddings)
├── test_recognition.py           # Embeddings, distance functions, normalization
├── test_database.py              # Schema DDL, CRUD operations, constraints, triggers
├── test_access_controller.py     # Decision boundaries, edge cases, safeguards
├── test_entry_logger.py          # Log writes, cooldown rate limiter, query filters
├── test_reports.py               # Confusion matrix, FAR/FRR, zero-division guards
└── test_integration.py           # Full simulated recognition lifecycle
```

---

## 3. Unit Test Specifications

### 3.1 Biometric Recognition Tests (`tests/test_recognition.py`)

```python
import numpy as np
import pytest
from modules.face_recognition import EmbeddingModel

def test_embedding_shape_and_type(mock_face_image):
    """Ensure embedding model returns a 512-element 1D float32 array."""
    model = EmbeddingModel.get_instance()
    embedding = model.generate_embedding(mock_face_image)
    
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (512,)
    assert embedding.dtype == np.float32

def test_embedding_l2_normalization(mock_face_image):
    """Ensure output vector has unit length (L2 norm == 1.0)."""
    model = EmbeddingModel.get_instance()
    embedding = model.generate_embedding(mock_face_image)
    norm = np.linalg.norm(embedding)
    assert np.isclose(norm, 1.0, atol=1e-5)

def test_cosine_distance_identical_vectors():
    """Identical vectors must yield cosine distance of 0.0."""
    v1 = np.random.randn(512).astype(np.float32)
    v1 /= np.linalg.norm(v1)
    
    dist = EmbeddingModel.compute_distance(v1, v1, metric="cosine")
    assert np.isclose(dist, 0.0, atol=1e-6)

def test_cosine_distance_orthogonal_vectors():
    """Orthogonal vectors must yield cosine distance of ~1.0."""
    v1 = np.zeros(512, dtype=np.float32)
    v2 = np.zeros(512, dtype=np.float32)
    v1[0] = 1.0
    v2[1] = 1.0
    
    dist = EmbeddingModel.compute_distance(v1, v2, metric="cosine")
    assert np.isclose(dist, 1.0, atol=1e-6)
```

---

### 3.2 Database & Persistence Tests (`tests/test_database.py`)

```python
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

def test_register_and_retrieve_resident(resident_mgr, dummy_vector):
    """Verify resident registration, serialization, and retrieval."""
    res_id = resident_mgr.register_resident(
        full_name="Test Resident",
        flat_number="A-101",
        contact_number="9999999999",
        image_bytes=b"fake_jpg_data",
        face_encoding=dummy_vector
    )
    assert res_id > 0
    
    resident = resident_mgr.get_resident_by_id(res_id)
    assert resident is not None
    assert resident.full_name == "Test Resident"
    assert resident.status == "ACTIVE"
    assert resident.face_encoding.shape == (512,)
    assert np.allclose(resident.face_encoding, dummy_vector)

def test_duplicate_resident_detection(resident_mgr, dummy_vector):
    """System must detect near-duplicate facial embeddings."""
    resident_mgr.register_resident(
        full_name="Original Resident",
        flat_number="B-202",
        contact_number=None,
        image_bytes=b"fake_jpg_data",
        face_encoding=dummy_vector
    )
    
    # Check duplicate with the exact same vector
    duplicate = resident_mgr.check_duplicate(dummy_vector, threshold=0.35)
    assert duplicate is not None
    assert duplicate.full_name == "Original Resident"

def test_deactivate_resident(resident_mgr, dummy_vector):
    """Deactivated resident must be excluded from get_all_active_residents()."""
    res_id = resident_mgr.register_resident("Deactivate Me", "C-303", None, b"...", dummy_vector)
    resident_mgr.set_resident_status(res_id, "INACTIVE")
    
    active_ids = [r.resident_id for r in resident_mgr.get_all_active_residents()]
    assert res_id not in active_ids
```

---

### 3.3 Access Controller Tests (`tests/test_access_controller.py`)

```python
import pytest
import numpy as np
from modules.access_controller import AccessController, DecisionEnum
from modules.resident_manager import Resident

def test_evaluate_face_confident_match(dummy_vector):
    """Distance <= 0.40 must result in ENTRY_ALLOWED (Green)."""
    controller = AccessController(accept_threshold=0.40, review_threshold=0.55)
    resident = Resident(1, "Alice", "A-1", None, "path.jpg", dummy_vector, "ACTIVE", None, None)
    
    # Probe is identical (distance = 0.0)
    result = controller.evaluate_face(probe_embedding=dummy_vector, active_residents=[resident])
    assert result.decision == DecisionEnum.ALLOWED
    assert result.resident.resident_id == 1
    assert result.distance <= 0.40

def test_evaluate_face_ambiguous_match(dummy_vector):
    """Distance between 0.40 and 0.55 must trigger VERIFICATION_REQUIRED (Yellow)."""
    controller = AccessController(accept_threshold=0.40, review_threshold=0.55)
    
    # Synthesize vector with distance ~0.48
    probe = dummy_vector.copy()
    probe[0] += 0.7
    probe /= np.linalg.norm(probe)
    
    resident = Resident(1, "Alice", "A-1", None, "path.jpg", dummy_vector, "ACTIVE", None, None)
    result = controller.evaluate_face(probe_embedding=probe, active_residents=[resident])
    
    if 0.40 < result.distance <= 0.55:
        assert result.decision == DecisionEnum.VERIFY

def test_evaluate_face_stranger_rejected(dummy_vector):
    """Distance > 0.55 must result in ENTRY_REJECTED (Red)."""
    controller = AccessController(accept_threshold=0.40, review_threshold=0.55)
    
    # Completely orthogonal vector (distance = 1.0)
    stranger = np.zeros(512, dtype=np.float32)
    stranger[100] = 1.0
    
    resident = Resident(1, "Alice", "A-1", None, "path.jpg", dummy_vector, "ACTIVE", None, None)
    result = controller.evaluate_face(probe_embedding=stranger, active_residents=[resident])
    assert result.decision == DecisionEnum.REJECTED
    assert result.resident is None

def test_evaluate_face_none_probe():
    """None probe (e.g. no face detected) must result in VERIFICATION_REQUIRED."""
    controller = AccessController()
    result = controller.evaluate_face(probe_embedding=None, active_residents=[])
    assert result.decision == DecisionEnum.VERIFY
    assert "No face detected" in result.reason
```

---

### 3.4 Report & Metrics Calculation Tests (`tests/test_reports.py`)

```python
import pytest
from modules.report_generator import ReportGenerator

def test_metrics_calculation_standard_case():
    """Verify standard TP, TN, FP, FN mathematical formulas."""
    metrics = ReportGenerator.calculate_metrics(tp=95, tn=50, fp=0, fn=5)
    
    # Accuracy = (95 + 50) / 150 = 96.67%
    assert pytest.approx(metrics["accuracy"], 0.01) == 96.67
    # FAR = 0 / 50 = 0.00%
    assert metrics["far"] == 0.0
    # FRR = 5 / 100 = 5.00%
    assert metrics["frr"] == 5.0
    # Precision = 95 / 95 = 100.0%
    assert metrics["precision"] == 100.0
    # Recall = 95 / 100 = 95.0%
    assert metrics["recall"] == 95.0

def test_metrics_zero_division_guard():
    """Metrics must handle zero denominator without crashing."""
    metrics = ReportGenerator.calculate_metrics(tp=0, tn=0, fp=0, fn=0)
    assert metrics["accuracy"] == 0.0
    assert metrics["far"] == 0.0
    assert metrics["frr"] == 0.0
    assert metrics["precision"] == 0.0
    assert metrics["recall"] == 0.0
```

---

## 4. PRD Functional Test Matrix (TC-01 through TC-12)

| Test ID | Scenario Description | Pre-Conditions | Test Procedure / Input | Expected Result | Automated Test Equivalent |
|---|---|---|---|---|---|
| **TC-01** | **Registered resident recognized** | Resident enrolled with active status | Present resident face under normal lighting | Green banner (`ENTRY_ALLOWED`), resident name & flat displayed, log saved | `test_evaluate_face_confident_match()` |
| **TC-02** | **Unknown person detected** | Subject not enrolled in database | Present unknown face | Red banner (`ENTRY_REJECTED`), unknown status, log saved | `test_evaluate_face_stranger_rejected()` |
| **TC-03** | **Borderline match** | Subject enrolled but distance in $0.40 - 0.55$ range | Present face with partial shadow or blur | Yellow banner (`VERIFICATION_REQUIRED`), guard prompted for manual check | `test_evaluate_face_ambiguous_match()` |
| **TC-04** | **No face in frame** | Camera active, empty room | Frame with 0 detected faces | No automatic approval; yellow alert *"No face detected"* | `test_evaluate_face_none_probe()` |
| **TC-05** | **Multiple faces in frame** | Camera active | 2 or more individuals in camera view | Both faces framed in yellow; system halts auto-grant; alerts guard | `test_multiple_faces_guard()` |
| **TC-06** | **Inactive resident entry** | Resident status set to `'INACTIVE'` | Enrolled resident attempts entry | Red banner (`ENTRY_REJECTED`), reason: *"Resident profile deactivated"* | `test_deactivated_resident_rejected()` |
| **TC-07** | **Webcam disconnected** | Camera streaming | Disconnect camera cable or pass invalid index | UI shows clean red alert banner; application does not crash | `test_camera_disconnect_handled()` |
| **TC-08** | **Duplicate registration** | Resident A already enrolled | Attempt to enroll Resident B with Resident A's photo | System displays duplicate warning showing Resident A's record | `test_duplicate_resident_detection()` |
| **TC-09** | **Recognition logging** | Completed recognition event | Any valid evaluation event occurs | Row inserted into `entry_logs` with timestamp, distance, and decision | `test_entry_logger_persists()` |
| **TC-10** | **Search resident** | 20+ residents enrolled | Query resident name "Sharma" in search bar | Filtered table displays matching profiles instantly | `test_resident_search_query()` |
| **TC-11** | **Filter entry history** | Logs populated with mixed decisions | Filter by date range and decision `'ENTRY_REJECTED'` | Grid renders only rejected events matching criteria | `test_filter_history_queries()` |
| **TC-12** | **Update resident photo** | Resident enrolled | Upload new photo and submit update | Embedding recalculated and updated in SQLite; image file updated | `test_update_photo_re_encodes()` |

---

## 5. Execution & CI Instructions

### 5.1 Running the Automated Test Suite

Execute all unit and integration tests from the project root:

```bash
# Run complete test suite with verbose output
pytest -v

# Run with test coverage report across application modules
pytest --cov=modules --cov=database --cov-report=term-missing

# Run a specific test module
pytest tests/test_access_controller.py -v

# Run only biometric recognition tests
pytest tests/test_recognition.py -v
```

### 5.2 Verification Checklist Before Submission
- [ ] All unit tests pass with zero failures: `pytest tests/` returns code 0.
- [ ] Code coverage exceeds 85% on core modules (`access_controller`, `resident_manager`, `entry_logger`, `report_generator`).
- [ ] Zero unhandled OpenCV or SQLite runtime exceptions.
- [ ] Offline benchmark run produces valid `reports/accuracy_report.md` with measured test dataset metrics.

