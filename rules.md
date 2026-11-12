# Engineering Rules, Standards, and Dependencies
# Smart Society Security System

---

## 1. What to Use (Approved Stack & Architectural Patterns)

### 1.1 Core Architecture & Principles
- **Layered Monolith**: Strictly separate the code into Presentation (`pages/`), Application (`modules/`), Computer Vision (`modules/webcam.py`, `face_detector.py`), Recognition (`modules/face_recognition.py`), and Data (`database/`).
- **Offline-First Execution**: The application must run completely self-contained on Windows 10/11 without contacting cloud endpoints, third-party CDNs, or external verification APIs during operation.
- **Assistance-Only Paradigm**: The software is an identification aid for guards, NOT an autonomous gate trigger. A positive match advises the security operator; it must not trigger physical gate relays without human oversight.

### 1.2 Approved Design Patterns
- **Singleton Pattern for Heavy Models**: Load the FaceNet / DeepFace neural weights exactly once at application startup into memory using `@st.cache_resource` or a thread-safe Python singleton. Never re-instantiate weights inside loop iterations or Streamlit page re-renders.
- **Context Managers (`with`)**: Use context managers for camera streams (`cv2.VideoCapture`), database transactions (`sqlite3.Connection`), and file I/O to guarantee prompt resource cleanup and avoid Windows file-lock errors.
- **Typed Data Transfer Objects (DTOs)**: Use Python `@dataclass(frozen=True)` or Pydantic models for exchanging data between layers (e.g., `Resident`, `DecisionResult`, `BenchmarkReport`).

### 1.3 Security & Cryptographic Standards
- **Password Hashing**: Store all administrative passwords hashed with `bcrypt` (work factor $\ge 12$). Salt strings must be cryptographically generated automatically.
- **Parameterized SQL**: All database operations must strictly use `?` parameter placeholders. Zero string formatting (`%`, `.format()`, or f-strings) in SQL queries.
- **Biometric Isolation**: Facial encodings must be stored as serialized binary blobs (`BLOB`) in SQLite; reference photographs stored locally in `data/residents/` with restricted OS file permissions.

---

## 2. What to Avoid (Forbidden Anti-Patterns & Practices)

| Category | Forbidden Practice | Why It Is Forbidden | Compliant Alternative |
|---|---|---|---|
| **Security** | Committing `.db`, `.env`, images, or model weights to Git | Exposes sensitive resident biometrics and credentials | Add all data folders to `.gitignore`; load via `.env` |
| **Security** | Plaintext or reversible password storage (e.g. MD5, Base64) | Extreme vulnerability; violation of biometric privacy standards | Use `bcrypt.hashpw()` and `bcrypt.checkpw()` |
| **Architecture** | Calling SQL queries or OpenCV directly in `pages/*.py` | Tight coupling; breaks unit testing and modularity | Call service methods in `modules/*.py` |
| **Performance** | Loading models inside the video processing loop | Triggers 2–5 second latency spikes per frame; freezes UI | Use singleton model wrapper with `@st.cache_resource` |
| **Performance** | Logging entry events on every processed video frame | Floods database with hundreds of redundant rows per second | Implement a temporal cooldown (e.g. 5–10 seconds per resident) |
| **Accuracy** | Claiming live dashboard counts as "Model Accuracy" | Real-time counts lack ground truth; false positives distort stats | Measure accuracy strictly on an isolated, labelled benchmark test dataset |
| **Reliability** | Copying thresholds from other embedding models | Distance metrics differ drastically between models (e.g. dlib vs. Facenet512) | Calibrate thresholds directly against model's specific cosine metric space |
| **Database** | Shared open SQLite connections across concurrent worker threads | SQLite throws `ProgrammingError: SQLite objects created in a thread can only be used in that same thread` | Use thread-safe connection factories or thread-local contexts |

---

## 3. Approved Libraries and Dependencies

### 3.1 Pinned `requirements.txt` Specification

```ini
# Core Application Framework
streamlit==1.35.0

# Computer Vision & Image Processing
opencv-python-headless==4.9.0.80
Pillow==10.3.0

# Deep Learning & Face Biometrics
deepface==0.0.92
tf-keras==2.16.0
tensorflow==2.16.1

# Numerical & Data Science
numpy==1.26.4
pandas==2.2.2
plotly==5.22.0

# Security & Utilities
bcrypt==4.1.3
python-dotenv==1.0.1

# Testing & Quality Assurance
pytest==8.2.1
pytest-mock==3.14.0
pytest-cov==5.0.0
```

> **Note on Windows Setup:** If hardware acceleration (CUDA) is not available, standard CPU TensorFlow wheels install and execute reliably on Windows 10/11 x64 systems. `opencv-python-headless` prevents GUI event conflicts with Streamlit.

---

## 4. Error Handling and Resilience Protocols

### 4.1 Camera Hardware Faults
- **Missing or Occupied Camera**: Wrap `cv2.VideoCapture(index)` with health checks:
  ```python
  cap = cv2.VideoCapture(camera_index)
  if not cap.isOpened():
      raise CameraUnavailableError(f"Webcam at index {camera_index} is unavailable or in use by another app.")
  ```
- **Stream Interruption**: If `cap.read()` yields `(False, None)`, display a clear UI banner: *"Camera disconnected. Attempting reconnection..."* and disable the recognition pipeline safely. Never raise unhandled fatal exceptions that crash the Streamlit server.

### 4.2 Computer Vision & Quality Assurance
- **Face Size Threshold**: Reject candidate faces smaller than $80 \times 80$ pixels. Small faces cause inaccurate embeddings.
- **Blur Detection via Laplacian Variance**: Compute $\sigma^2 = \text{Var}(\nabla^2 I)$. If $\sigma^2 < 100.0$, flag frame as blurred:
  - Outcome: `VERIFICATION_REQUIRED` (Yellow).
  - Reason: *"Face image blurry; hold still in front of camera."*
- **Multiple Faces in Frame**: When $>1$ face is detected:
  - Do not automatically grant `ENTRY_ALLOWED`.
  - Highlight each bounding box with a yellow warning border.
  - Reason: *"Multiple persons detected. Please approach one at a time."*

### 4.3 Evaluation & Numerical Safety
- **Zero-Division Safeguard**: In evaluation metrics (e.g., when $TP + FP = 0$), handle gracefully:
  ```python
  precision = (tp / (tp + fp) * 100) if (tp + fp) > 0 else 0.0
  far = (fp / (fp + tn) * 100) if (fp + tn) > 0 else 0.0
  ```
- **Corrupted Biometric Blob**: If SQLite returns an unpicklable or malformed embedding vector, log error, skip the record, and notify the administrator via the management console to re-enroll the resident.

---

## 5. General Operational Rules

1. **Informed Biometric Consent**: Before enrolling any resident, the administrator must confirm informed consent in accordance with privacy laws.
2. **Deterministic Threshold Configuration**: Threshold values (`ACCEPT_THRESHOLD = 0.40`, `REVIEW_THRESHOLD = 0.55`) must reside in `config/settings.py` or `.env`. Never hardcode numerical comparison boundaries within business logic.
3. **Database Migration Idempotency**: All SQL initialization scripts must utilize `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS`.
4. **Clean Exit & Signal Handling**: Always release OpenCV camera handles when navigating away from the live monitoring page to prevent Windows hardware lockups.
5. **No Data Loss on Resident Deactivation**: Setting a resident's status to `INACTIVE` must instantly block automatic recognition access while completely preserving past entry log history and audit trails.

