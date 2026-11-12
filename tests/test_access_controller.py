import pytest
import numpy as np
from modules.access_controller import AccessController, DecisionEnum
from modules.resident_manager import Resident

def test_evaluate_face_confident_match(dummy_vector):
    """Distance <= 0.40 must result in ENTRY_ALLOWED (Green)."""
    controller = AccessController(accept_threshold=0.40, review_threshold=0.55)
    resident = Resident(1, "Alice", "A-1", None, "path.jpg", dummy_vector, "ACTIVE", "now", "now")
    
    # Probe is identical (distance = 0.0)
    result = controller.evaluate_face(probe_embedding=dummy_vector, active_residents=[resident])
    assert result.decision == DecisionEnum.ALLOWED
    assert result.resident.resident_id == 1
    assert result.distance <= 0.40

def test_evaluate_face_stranger_rejected(dummy_vector):
    """Distance > 0.55 must result in ENTRY_REJECTED (Red)."""
    controller = AccessController(accept_threshold=0.40, review_threshold=0.55)
    
    # Orthogonal vector (distance = 1.0)
    stranger = np.zeros(512, dtype=np.float32)
    stranger[100] = 1.0
    
    resident = Resident(1, "Alice", "A-1", None, "path.jpg", dummy_vector, "ACTIVE", "now", "now")
    result = controller.evaluate_face(probe_embedding=stranger, active_residents=[resident])
    assert result.decision == DecisionEnum.REJECTED
    assert result.resident is None
    assert result.distance > 0.55

def test_evaluate_face_none_probe():
    """None probe (e.g. no face detected) must result in VERIFICATION_REQUIRED."""
    controller = AccessController()
    result = controller.evaluate_face(probe_embedding=None, active_residents=[])
    assert result.decision == DecisionEnum.VERIFY
    assert "No clear face" in result.reason

def test_evaluate_face_empty_residents(dummy_vector):
    """If no active residents exist in gallery, must return ENTRY_REJECTED."""
    controller = AccessController()
    result = controller.evaluate_face(probe_embedding=dummy_vector, active_residents=[])
    assert result.decision == DecisionEnum.REJECTED

