import cv2
import numpy as np
from typing import Optional, Tuple
from config.settings import DEFAULT_CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT

class WebcamCapture:
    """
    Encapsulates OpenCV VideoCapture with connection management, frame resizing,
    and safe resource disposal.
    """
    def __init__(self, camera_index: int = DEFAULT_CAMERA_INDEX):
        self.camera_index = camera_index
        self.cap: Optional[cv2.VideoCapture] = None

    def start(self) -> bool:
        """Initializes the camera stream. Returns True if successfully opened."""
        if self.cap is not None and self.cap.isOpened():
            return True
        self.cap = cv2.VideoCapture(self.camera_index)
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
            return True
        return False

    def is_opened(self) -> bool:
        return self.cap is not None and self.cap.isOpened()

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Reads a single frame from the camera.
        Returns: (success_bool, frame_ndarray_rgb_or_none)
        """
        if not self.is_opened():
            if not self.start():
                return False, None
        
        success, frame = self.cap.read()
        if not success or frame is None:
            return False, None
        
        # Convert BGR (OpenCV standard) to RGB (Streamlit / PIL standard)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return True, frame_rgb

    def stop(self) -> None:
        """Releases the camera device."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

