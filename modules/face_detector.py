import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any
from config.settings import MIN_FACE_SIZE, BLUR_THRESHOLD, BASE_DIR

class FaceDetector:
    """
    OpenCV-based face detection with image quality guards (minimum size, blur detection).
    """
    def __init__(self):
        # Prefer locally bundled XML cascade inside models/
        bundled_xml = BASE_DIR / "models" / "haarcascade_frontalface_default.xml"
        if bundled_xml.exists():
            cascade_path = str(bundled_xml)
        elif hasattr(cv2, "data") and hasattr(cv2.data, "haarcascades"):
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        else:
            cascade_path = "haarcascade_frontalface_default.xml"

        self.cascade = cv2.CascadeClassifier(cascade_path)
        if self.cascade.empty():
            # Attempt to re-load from bundled models directory
            if bundled_xml.exists():
                self.cascade.load(str(bundled_xml))

    def calculate_blur_score(self, face_rgb: np.ndarray) -> float:
        """
        Computes the variance of the Laplacian (Laplacian variance) on grayscale image.
        Scores lower than BLUR_THRESHOLD indicate blurry/unusable images.
        """
        if face_rgb is None or face_rgb.size == 0:
            return 0.0
        gray = cv2.cvtColor(face_rgb, cv2.COLOR_RGB2GRAY)
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())

    def detect_faces(self, frame_rgb: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detects faces in an RGB frame.
        Returns a list of bounding boxes: [(x, y, w, h), ...]
        """
        if frame_rgb is None or frame_rgb.size == 0:
            return []
        gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
        faces = self.cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(MIN_FACE_SIZE, MIN_FACE_SIZE)
        )
        return [tuple(box) for box in faces]

    def assess_face_quality(self, frame_rgb: np.ndarray, bbox: Tuple[int, int, int, int]) -> Dict[str, Any]:
        """
        Evaluates quality metrics for a detected face box.
        """
        x, y, w, h = bbox
        h_frame, w_frame, _ = frame_rgb.shape
        
        # Ensure within bounds
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(w_frame, x + w), min(h_frame, y + h)
        face_crop = frame_rgb[y1:y2, x1:x2]
        
        blur_score = self.calculate_blur_score(face_crop)
        is_blurred = blur_score < BLUR_THRESHOLD
        is_size_ok = (w >= MIN_FACE_SIZE) and (h >= MIN_FACE_SIZE)

        return {
            "bbox": (x1, y1, x2 - x1, y2 - y1),
            "face_crop": face_crop,
            "blur_score": blur_score,
            "is_blurred": is_blurred,
            "is_size_ok": is_size_ok,
            "is_acceptable": (not is_blurred) and is_size_ok
        }

    def draw_overlays(
        self,
        frame_rgb: np.ndarray,
        faces_data: List[Dict[str, Any]],
        primary_color: Tuple[int, int, int] = (0, 255, 0),
        label: str = ""
    ) -> np.ndarray:
        """
        Draws bounding boxes and labels on a copy of the frame.
        """
        annotated = frame_rgb.copy()
        for item in faces_data:
            x, y, w, h = item["bbox"]
            cv2.rectangle(annotated, (x, y), (x + w, y + h), primary_color, 2)
            if label:
                cv2.putText(
                    annotated,
                    label,
                    (x, max(20, y - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    primary_color,
                    2
                )
        return annotated

