import numpy as np
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Tuple
from modules.resident_manager import Resident
from config.settings import ACCEPT_THRESHOLD, REVIEW_THRESHOLD

class DecisionEnum(str, Enum):
    ALLOWED = "ENTRY_ALLOWED"
    REJECTED = "ENTRY_REJECTED"
    VERIFY = "VERIFICATION_REQUIRED"

@dataclass
class DecisionResult:
    decision: DecisionEnum
    resident: Optional[Resident]
    distance: float
    confidence_score: float
    reason: str

class AccessController:
    """
    Evaluates face embeddings against the gallery of active residents
    based on calibrated threshold boundaries.
    """
    def __init__(
        self,
        accept_threshold: float = ACCEPT_THRESHOLD,
        review_threshold: float = REVIEW_THRESHOLD
    ):
        self.accept_threshold = accept_threshold
        self.review_threshold = review_threshold

    @staticmethod
    def compute_cosine_distance(u: np.ndarray, v: np.ndarray) -> float:
        """
        Calculates Cosine Distance: 1.0 - (u . v) / (||u|| * ||v||)
        Bounded between 0.0 (identical) and 2.0 (opposite).
        """
        u_flat = u.flatten().astype(np.float32)
        v_flat = v.flatten().astype(np.float32)
        dot = np.dot(u_flat, v_flat)
        norm_u = np.linalg.norm(u_flat)
        norm_v = np.linalg.norm(v_flat)
        if norm_u == 0 or norm_v == 0:
            return 1.0
        similarity = float(dot / (norm_u * norm_v))
        similarity = max(-1.0, min(1.0, similarity))
        return 1.0 - similarity

    def find_best_match(
        self,
        probe_embedding: np.ndarray,
        active_residents: List[Resident]
    ) -> Tuple[Optional[Resident], float]:
        """
        Finds the resident with minimum distance to the probe embedding.
        """
        if not active_residents:
            return None, 1.0

        best_resident = None
        min_distance = float("inf")

        for resident in active_residents:
            dist = self.compute_cosine_distance(probe_embedding, resident.face_encoding)
            if dist < min_distance:
                min_distance = dist
                best_resident = resident

        return best_resident, float(min_distance)

    def evaluate_face(
        self,
        probe_embedding: Optional[np.ndarray],
        active_residents: List[Resident],
        quality_reason: Optional[str] = None
    ) -> DecisionResult:
        """
        Evaluates a candidate probe embedding against enrolled active residents.
        """
        if probe_embedding is None:
            return DecisionResult(
                decision=DecisionEnum.VERIFY,
                resident=None,
                distance=1.0,
                confidence_score=0.0,
                reason=quality_reason or "No clear face detected in frame."
            )

        if not active_residents:
            return DecisionResult(
                decision=DecisionEnum.REJECTED,
                resident=None,
                distance=1.0,
                confidence_score=0.0,
                reason="No active registered residents in database."
            )

        best_resident, min_distance = self.find_best_match(probe_embedding, active_residents)

        # Convert distance to intuitive confidence percentage: 1.0 - (distance / 2.0)
        confidence = max(0.0, min(100.0, (1.0 - min_distance) * 100.0))

        # Zone 1: Confident Match (Green)
        if min_distance <= self.accept_threshold:
            return DecisionResult(
                decision=DecisionEnum.ALLOWED,
                resident=best_resident,
                distance=min_distance,
                confidence_score=round(confidence, 1),
                reason=f"Identity confirmed: {best_resident.full_name} ({best_resident.flat_number})"
            )

        # Zone 2: Ambiguous / Borderline Match (Yellow)
        if min_distance <= self.review_threshold:
            name = best_resident.full_name if best_resident else "Unknown"
            return DecisionResult(
                decision=DecisionEnum.VERIFY,
                resident=best_resident,
                distance=min_distance,
                confidence_score=round(confidence, 1),
                reason=f"Borderline match with {name}. Manual guard verification required."
            )

        # Zone 3: Stranger / Unregistered (Red)
        return DecisionResult(
            decision=DecisionEnum.REJECTED,
            resident=None,
            distance=min_distance,
            confidence_score=round(confidence, 1),
            reason="Unrecognized individual. Please direct to visitor gate."
        )

