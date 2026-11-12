# Project Implementation Phases & Roadmap
# Smart Society Security System

---

## Roadmap Overview

The Smart Society Security System implementation is structured into **8 sequential phases** designed to transition from core computer-vision foundations to biometric engine calibration, relational persistence, interactive UI delivery, and rigorous offline benchmark evaluation.

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 0: Environment Setup & Project Scaffolding            │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Computer Vision & Video Capture Pipeline           │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: FaceNet Biometric Engine & Calibration             │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: SQLite Persistence & Resident Management           │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Access Decision Engine & Event Logging Guard       │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: Streamlit Multi-Page Security Dashboard            │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 6: Automated Testing & Benchmark Evaluation           │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 7: System Hardening, Audit & Final Demonstration      │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 0: Environment Setup & Scaffolding (Day 1 - Morning)

### Objectives
Establish a clean, reproducible Python 3.10+ virtual environment on Windows 10/11, scaffold directory structure, and initialize project configuration.

### Tasks
- [ ] Create Python virtual environment (`python -m venv venv`) and activate.
- [ ] Create `requirements.txt` with pinned versions (OpenCV, DeepFace, Streamlit, SQLite, NumPy, Pandas, Plotly, Pytest, Bcrypt).
- [ ] Set up directory structure: `config/`, `database/`, `modules/`, `pages/`, `data/residents/`, `data/snapshots/`, `tests/`, `reports/`.
- [ ] Configure `.gitignore` to exclude SQLite database files (`*.db`), biometrics/photos (`data/`), model weights, and `.env`.
- [ ] Create `config/settings.py` to centralize paths, thresholds, and camera settings.
- [ ] Create `.env.example` file.

### Deliverables
- Working virtual environment with all installed libraries.
- Complete folder tree with `.gitkeep` files where appropriate.
- Verified `config/settings.py`.

---

## Phase 1: Computer Vision & Video Pipeline (Day 1 - Afternoon)

### Objectives
Implement webcam frame acquisition, graceful camera error handling, and robust facial detection with image quality checks.

### Tasks
- [ ] Implement `modules/webcam.py` with `WebcamCapture` class wrapping `cv2.VideoCapture`.
- [ ] Add camera device enumeration and connection validation.
- [ ] Implement `modules/face_detector.py` using OpenCV Haar Cascade or DNN face detector.
- [ ] Implement bounding box extraction and face cropping utilities ($160 \times 160$ alignment).
- [ ] Add image quality guards:
  - Minimum bounding box size ($80 \times 80$ px).
  - Blur score validation using Laplacian variance ($\sigma^2 \ge 100$).
- [ ] Write unit tests for frame capture and face cropping (`tests/test_webcam.py`).

### Deliverables
- Stable webcam feed class supporting clean start/stop.
- Bounding box and cropped face extractor with blur detection.

---

## Phase 2: FaceNet Biometric Engine & Calibration (Day 2)

### Objectives
Integrate the deep face recognition model, extract standardized normalized embeddings, and calibrate matching distance thresholds.

### Tasks
- [ ] Implement `modules/face_recognition.py` wrapping `Facenet512` model backend.
- [ ] Implement singleton model loader to guarantee weights load into RAM only once.
- [ ] Build `generate_embedding(face_img: np.ndarray) -> np.ndarray` (512-d normalized vector).
- [ ] Implement distance calculation functions: Cosine Distance and Euclidean L2 Distance.
- [ ] Conduct threshold calibration on sample pairs to confirm operating boundaries:
  - `ACCEPT_THRESHOLD = 0.40`
  - `REVIEW_THRESHOLD = 0.55`
- [ ] Write unit tests for embedding generation and vector normalization (`tests/test_recognition.py`).

### Deliverables
- Reusable `EmbeddingModel` service module.
- Documented threshold calibration guide in `models/README.md`.

---

## Phase 3: SQLite Persistence & Resident Management (Day 3)

### Objectives
Implement thread-safe SQLite persistence layer and full CRUD workflows for resident profiles and biometric encodings.

### Tasks
- [ ] Author `database/schema.sql` defining `admins`, `residents`, `entry_logs`, and `system_config`.
- [ ] Implement `database/db.py` connection factory with foreign key enforcement and row factories.
- [ ] Implement `modules/resident_manager.py`:
  - `register_resident(name, flat, contact, image, embedding)`
  - `get_all_active_residents()`
  - `update_resident()`, `deactivate_resident()`
  - `check_duplicate(new_embedding, threshold=0.35)`
- [ ] Store resident photos securely in `data/residents/{resident_id}.jpg`.
- [ ] Write integration tests for database CRUD and duplicate detection (`tests/test_database.py`).
- [ ] Enroll baseline dataset of at least 20 consented resident profiles.

### Deliverables
- Fully initialized SQLite database.
- Complete Resident Management service layer.
- Populated database with 20 registered resident test profiles.

---

## Phase 4: Access Decision Engine & Logging Guard (Day 4)

### Objectives
Build the access decision logic with three-tier classification (Green / Yellow / Red) and rate-limited entry logging.

### Tasks
- [ ] Implement `modules/access_controller.py`:
  - `evaluate_face(probe_embedding, active_residents)`
  - Handle edge cases: No face detected, multiple faces, inactive resident profiles.
  - Return typed `DecisionResult` with distance, confidence, and human-readable reason.
- [ ] Implement `modules/entry_logger.py`:
  - `log_attempt()` with database transaction commits.
  - Implement 5-second per-resident cooldown cache to prevent frame-rate flood.
  - Query functions: `get_recent_logs()`, `search_logs(filters)`.
- [ ] Write unit and scenario tests for decision boundaries (`tests/test_access_controller.py`).

### Deliverables
- Reliable 3-state access decision engine.
- Cooldown-protected persistent event logging module.

---

## Phase 5: Streamlit Multi-Page Security Dashboard (Day 5)

### Objectives
Develop an intuitive, responsive Streamlit dashboard tailored to security guards and administrators.

### Tasks
- [ ] Implement `app.py` with multi-page navigation and session state management.
- [ ] Build **Screen 1 — Dashboard (`pages/dashboard.py`)**:
  - Metric cards: Total Residents, Today's Attempts, Approvals, Rejections, Manual Reviews.
  - Camera connection status banner and recent activity ticker.
- [ ] Build **Screen 2 — Live Monitoring (`pages/live_monitoring.py`)**:
  - Live video stream with overlay boxes.
  - Large color-coded outcome alert card (Green/Yellow/Red).
  - Identified resident details and manual override buttons.
- [ ] Build **Screen 3 — Register Resident (`pages/register_resident.py`)**:
  - Form with input fields, photo upload/webcam capture, quality check, and duplicate warning.
- [ ] Build **Screen 4 — Manage Residents (`pages/manage_residents.py`)**:
  - Searchable table, edit modal, status toggle (Active/Inactive), photo update.
- [ ] Build **Screen 5 — Entry History (`pages/entry_history.py`)**:
  - Filterable audit log with date range, status, and flat number search.
- [ ] Build **Screen 6 — Analytics & Reports (`pages/analytics.py`)**:
  - Plotly visualization of entry trends and model benchmark metrics.

### Deliverables
- Fully functional multi-page web application running locally via `streamlit run app.py`.

---

## Phase 6: Automated Testing & Benchmark Evaluation (Day 6)

### Objectives
Execute offline quantitative evaluation against isolated 150-sample benchmark dataset and calculate academic metrics.

### Tasks
- [ ] Prepare evaluation test dataset:
  - 100 registered resident test attempts (5 per resident across 20 residents).
  - 50 unknown intruder test attempts (5 per person across 10 strangers).
- [ ] Implement `modules/report_generator.py`:
  - Automated batch inference runner.
  - Computes TP, TN, FP, FN, Accuracy, FAR, FRR, Precision, Recall, Average Latency.
- [ ] Generate confusion matrix and Plotly ROC / FAR-FRR trade-off curves.
- [ ] Run Pytest automated test suite across all modules (`pytest tests/ --cov=modules`).
- [ ] Export final markdown report to `reports/accuracy_report.md`.

### Deliverables
- Comprehensive evaluation report with real measured numbers.
- Automated Pytest test suite with >85% code coverage.

---

## Phase 7: System Hardening, Audit & Demonstration (Day 7)

### Objectives
Verify security protocols, conduct end-to-end user acceptance tests, finalize user documentation, and prepare presentation.

### Tasks
- [ ] Conduct end-to-end walkthrough verifying all 12 Functional Test Cases (TC-01 through TC-12).
- [ ] Verify biometric data privacy: Ensure `.gitignore` prevents leaks and passwords are hashed.
- [ ] Verify error handling: Disconnect camera mid-stream and confirm graceful recovery without crash.
- [ ] Author comprehensive `README.md` with Windows installation commands, quickstart guide, and architecture diagram.
- [ ] Rehearse live demonstration scenario (admitting resident, rejecting stranger, manual review).

### Deliverables
- Polished, bug-free codebase ready for evaluation.
- Complete documentation suite (`README.md`, `DataBase.md`, `rules.md`, `phase.md`, `design.md`, `testing.md`).
- Live demonstration rehearsal completed.

