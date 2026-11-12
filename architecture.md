# Architecture Document
# Smart Society Security System

---

## High-Level Design (HLD)

### System Overview

The Smart Society Security System is a local, offline-first Python application that uses facial recognition to assist security personnel at a residential society entrance. It runs entirely on a Windows laptop with a built-in webcam and requires no cloud connectivity after initial setup.

### Architecture Style

**Layered Monolithic Architecture** — a single Python application divided into five distinct layers, each with a clear responsibility boundary.

```
┌────────────────────────────────────────────────┐
│              Presentation Layer                │
│         (Streamlit Multi-Page App)             │
├────────────────────────────────────────────────┤
│              Application Layer                 │
│   (Business Logic, Access Control, Logging)    │
├────────────────────────────────────────────────┤
│           Computer-Vision Layer                │
│    (OpenCV Capture, Detection, Preprocessing)  │
├────────────────────────────────────────────────┤
│             Recognition Layer                  │
│   (Embedding Generation, Matching, Thresholds) │
├────────────────────────────────────────────────┤
│               Data Layer                       │
│        (SQLite DB, Local File Storage)         │
└────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Components | Responsibility |
|---|---|---|
| Presentation | Streamlit pages | UI rendering, user input, navigation |
| Application | Resident manager, access controller, entry logger, report generator | Business rules, orchestration |
| Computer Vision | Webcam capture, face detector, image preprocessor | Frame acquisition, face detection, quality checks |
| Recognition | Embedding model, matcher, threshold evaluator | Embedding generation and distance-based matching |
| Data | SQLite, local file system | Persistence of profiles, embeddings, logs, images |

### Key Data Flows

**Live Recognition Flow**
```
Webcam → Frame Capture → Face Detection → Quality Check
       → Embedding Generation → DB Embedding Lookup
       → Distance Calculation → Threshold Evaluation
       → Decision (GREEN / YELLOW / RED) → Entry Log Write → UI Display
```

**Resident Registration Flow**
```
Admin Form → Webcam Capture / Image Upload → Face Validation
           → Embedding Generation → Duplicate Check
           → SQLite Write → Image Save → Success Confirmation
```

**Report Generation Flow**
```
Test Dataset → Batch Recognition → TP / TN / FP / FN Counts
             → Metric Calculation → Pandas DataFrame → Plotly Charts → Export
```

---

## Low-Level Design (LLD)

### Module Breakdown

#### `config/settings.py`
- Global constants: thresholds (`ACCEPT_THRESHOLD`, `REVIEW_THRESHOLD`), camera index, image dimensions, cooldown period, database path, model path.
- Loaded once at startup; never hard-coded inside modules.

#### `database/db.py`
- `get_connection()` — returns a thread-safe SQLite connection.
- `init_db()` — runs `schema.sql` on first launch.
- Context manager for auto-commit / rollback.

#### `modules/webcam.py`
- `WebcamCapture` class — wraps `cv2.VideoCapture`.
- Methods: `start()`, `stop()`, `read_frame()` → `np.ndarray | None`.
- Handles camera index selection, reconnection, and error states.

#### `modules/face_detector.py`
- `FaceDetector` class — wraps a Haar cascade or DNN-based detector.
- `detect(frame)` → `list[BoundingBox]`
- `crop_face(frame, bbox)` → `np.ndarray`
- Quality check: minimum face size, blur score (Laplacian variance).

#### `modules/face_recognition.py`
- `EmbeddingModel` class — loads the pretrained FaceNet-compatible ONNX model.
- `generate_embedding(face_img)` → `np.ndarray` (128-d or 512-d vector)
- Singleton pattern — model loaded once and reused.

#### `modules/resident_manager.py`
- CRUD operations on the `residents` table.
- `register_resident(data, embedding)` → `resident_id`
- `get_all_active_residents()` → `list[Resident]`
- `update_resident(id, data)`, `deactivate_resident(id)`, `delete_resident(id)`
- `check_duplicate(embedding, threshold)` → `bool`

#### `modules/access_controller.py`
- `decide_entry(face_embedding, active_residents)` → `Decision`
- `find_best_match(embedding, residents)` → `MatchResult | None`
- Implements threshold logic: accept / review / reject.
- Guards: no face, multiple faces, inactive profile, stale frame.

#### `modules/entry_logger.py`
- `log_attempt(resident_id, distance, decision, reason, snapshot_path)` → `log_id`
- Cooldown guard: suppresses duplicate logs within configurable window.
- `get_recent_logs(n)`, `search_logs(filters)`.

#### `modules/report_generator.py`
- `run_evaluation(test_dataset_path)` → `MetricsResult`
- Computes TP, TN, FP, FN, accuracy, FAR, FRR, precision, recall.
- Returns a Pandas DataFrame for chart rendering.

#### `pages/*.py`
- Each page is a standalone Streamlit module imported by `app.py`.
- Pages call Application-layer modules; they never access the DB or model directly.

### Component Interaction Diagram

```
app.py
 ├── pages/dashboard.py          → entry_logger, resident_manager
 ├── pages/live_monitoring.py    → webcam, face_detector, face_recognition,
 │                                  access_controller, entry_logger
 ├── pages/register_resident.py  → webcam, face_detector, face_recognition,
 │                                  resident_manager
 ├── pages/manage_residents.py   → resident_manager
 ├── pages/entry_history.py      → entry_logger
 └── pages/analytics.py          → report_generator
```

---

## Folder Structure

```
smart-society-security/
│
├── app.py                        # Streamlit entry point, page router
├── requirements.txt              # Pinned dependencies
├── README.md                     # Setup and usage guide
├── .env.example                  # Environment variable template
├── .gitignore                    # Excludes DB, images, model weights, .env
│
├── config/
│   └── settings.py               # Thresholds, paths, camera index, constants
│
├── database/
│   ├── db.py                     # Connection manager, init_db()
│   └── schema.sql                # CREATE TABLE statements
│
├── modules/
│   ├── webcam.py                 # WebcamCapture class
│   ├── face_detector.py          # FaceDetector class
│   ├── face_recognition.py       # EmbeddingModel class
│   ├── resident_manager.py       # Resident CRUD
│   ├── access_controller.py      # Decision engine
│   ├── entry_logger.py           # Log writer and reader
│   └── report_generator.py      # Metrics and evaluation
│
├── pages/
│   ├── dashboard.py              # Screen 1
│   ├── live_monitoring.py        # Screen 2
│   ├── register_resident.py      # Screen 3
│   ├── manage_residents.py       # Screen 4
│   ├── entry_history.py          # Screen 5
│   └── analytics.py              # Screen 6
│
├── models/
│   └── README.md                 # Download instructions for model weights
│
├── data/
│   ├── residents/                # Profile photographs (gitignored)
│   └── snapshots/                # Optional recognition snapshots (gitignored)
│
├── tests/
│   ├── conftest.py               # Shared fixtures
│   ├── test_recognition.py       # Embedding and matching tests
│   ├── test_database.py          # DB CRUD tests
│   ├── test_access_controller.py # Decision logic tests
│   └── test_reports.py           # Metrics calculation tests
│
└── reports/
    └── accuracy_report.md        # Final measured test results
```

---

## Tech Stack

| Category | Technology | Version | Purpose |
|---|---|---|---|
| Language | Python | 3.10+ | Core application |
| UI Framework | Streamlit | 1.35+ | Multi-page dashboard and controls |
| Computer Vision | OpenCV (`opencv-python`) | 4.9+ | Webcam capture, face detection, image ops |
| Face Embeddings | `deepface` or `facenet-pytorch` | latest stable | Pretrained FaceNet-compatible model |
| Numerical | NumPy | 1.26+ | Embedding vectors, distance calculations |
| Image Handling | Pillow | 10.x | Image loading, resizing, format conversion |
| Database | SQLite (stdlib `sqlite3`) | built-in | Resident profiles and entry logs |
| Data Analysis | Pandas | 2.x | Test result aggregation, metric tables |
| Charts | Plotly | 5.x | Interactive dashboard charts |
| Testing | Pytest | 8.x | Unit and integration tests |
| Password Hashing | `bcrypt` | 4.x | Admin password storage |
| Environment | `python-dotenv` | 1.x | Load `.env` config at runtime |

### Model Choice
- **Recommended:** `deepface` with the `Facenet512` backend (512-d embeddings, cosine distance).
- Fallback: `face_recognition` library (dlib-based, 128-d Euclidean distance).
- Document the chosen model, version, and licensing in `models/README.md`.
- Thresholds must be calibrated against the chosen model's distance space — do not copy thresholds from a different model.

### Why These Choices
- **Streamlit** — zero-boilerplate Python UI, ideal for academic prototypes; no HTML/CSS required.
- **SQLite** — serverless, file-based, ships with Python stdlib; no install overhead.
- **OpenCV** — industry standard for real-time video processing on Windows.
- **deepface** — single-library wrapper around multiple pretrained models; reduces integration effort.
- **Plotly** — Streamlit-native chart library with interactive support.
