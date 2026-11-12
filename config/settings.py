import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESIDENTS_DIR = DATA_DIR / "residents"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"
REPORTS_DIR = BASE_DIR / "reports"
DB_PATH = BASE_DIR / "database" / "security.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"

# Recognition Thresholds (Calibrated for Cosine Distance space [0.0 - 2.0])
# Distance <= ACCEPT_THRESHOLD: ENTRY_ALLOWED (Green)
ACCEPT_THRESHOLD = float(os.getenv("ACCEPT_THRESHOLD", "0.40"))

# ACCEPT_THRESHOLD < Distance <= REVIEW_THRESHOLD: VERIFICATION_REQUIRED (Yellow)
# Distance > REVIEW_THRESHOLD: ENTRY_REJECTED (Red)
REVIEW_THRESHOLD = float(os.getenv("REVIEW_THRESHOLD", "0.55"))

# Temporal Cooldown guard to avoid frame-by-frame duplicate logging (in seconds)
EVENT_COOLDOWN_SECONDS = int(os.getenv("EVENT_COOLDOWN_SECONDS", "5"))

# Camera Configuration
DEFAULT_CAMERA_INDEX = int(os.getenv("DEFAULT_CAMERA_INDEX", "0"))
FRAME_WIDTH = int(os.getenv("FRAME_WIDTH", "640"))
FRAME_HEIGHT = int(os.getenv("FRAME_HEIGHT", "480"))

# Quality Assurance Criteria
MIN_FACE_SIZE = 80  # Minimum face width/height in pixels
BLUR_THRESHOLD = 80.0  # Laplacian variance threshold

# Model Backend Configuration
MODEL_NAME = os.getenv("FACE_MODEL_NAME", "Facenet512")
EMBEDDING_DIM = 512

# Ensure required directories exist at boot
RESIDENTS_DIR.mkdir(parents=True, exist_ok=True)
SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
(BASE_DIR / "database").mkdir(parents=True, exist_ok=True)

