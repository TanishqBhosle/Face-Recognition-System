# Smart Society Security System
## AI-Based Facial Recognition and Access Management

---

## 1. Project Overview

The Smart Society Security System is a local, offline-first Python web application designed to assist security personnel at the entrance gate of a residential housing society. Using a standard laptop webcam, the system captures real-time video, detects faces, compares them against a database of registered residents using deep learning embeddings, and displays an immediate, color-coded access recommendation.

### The Problem It Solves
Traditional residential gate security depends on manual visitor logs and guard memory. This often leads to entry delays, inconsistent verification, human error, and incomplete paper records. 

### The Solution
This project provides a digital assistance station that:
- Identifies enrolled residents automatically in under 100 milliseconds.
- Flags unknown individuals and strangers for gate inspection.
- Identifies low-quality, ambiguous, or blurred images and requests manual guard verification.
- Stores complete, tamper-resistant access audit trails in a local SQLite database.
- Evaluates biometric accuracy against an isolated benchmark test dataset.

**Important Operational Note:** This application is strictly an identification-assistance tool. A facial match alone does not mechanically unlock gates; the security guard remains in full control of all physical entry decisions.

---

## 2. How the System Works

The recognition pipeline executes locally on the machine in five sequential steps:

1. **Video Capture:** The application accesses the built-in webcam using OpenCV and reads incoming frames.
2. **Face Detection & Quality Checks:** The system locates faces in the frame. It checks that the face is at least 80 by 80 pixels and verifies sharpness using Laplacian variance to prevent blurred images from causing incorrect decisions.
3. **Biometric Feature Extraction:** The cropped face image is converted into a 512-dimensional normalized mathematical vector (embedding) using a FaceNet-compatible deep learning architecture.
4. **Distance Matching:** The system calculates the Cosine Distance between the captured face vector and all active resident vectors stored in SQLite. A distance of 0.0 means identical, while values above 0.55 represent strangers.
5. **Decision & Logging:** The system outputs one of three clear decisions on screen and writes an audit record to the database with a built-in cooldown mechanism to prevent frame-by-frame log duplication.

---

## 3. Decision Framework

The application classifies every recognition attempt into one of three distinct operational states:

| Status | Color | Distance Range | Description and Guard Action |
|---|---|---|---|
| **ENTRY ALLOWED** | Green | Distance <= 0.40 | High-confidence match to an active resident. The resident's name, flat number, and reference photo appear on screen. The guard facilitates entry. |
| **VERIFICATION REQUIRED** | Yellow | 0.40 < Distance <= 0.55 | Ambiguous match, poor lighting, slight angle, or motion blur. The guard is prompted to verify identity manually by checking a photo ID or flat number. |
| **ENTRY REJECTED** | Red | Distance > 0.55 | The individual does not match any registered resident profile. The guard directs the individual to the visitor sign-in protocol. |

**Additional Safety Rules:**
- If no face is visible, the system remains in standby and issues no approval.
- If multiple individuals appear in the frame simultaneously, the system withholds automatic admission and alerts the guard.
- Deactivated resident profiles are permanently blocked from receiving automatic positive recognition.

---

## 4. Key Application Modules

The system provides six primary functional screens accessible via the navigation sidebar:

### 1. Operations Dashboard
Displays daily entry statistics, active resident count, ratio of allowed vs. rejected attempts, live camera node connectivity status, and a real-time activity stream of the last 10 gate events.

### 2. Live Entrance Monitoring
The primary screen for security guards on duty. Offers live video streaming, instant webcam snapshots, or probe image uploads. Displays large, high-visibility decision cards, matched resident details, confidence telemetry, and manual override buttons (Force Admit / Force Deny).

### 3. Resident Registration
Allows administrators to enroll new residents. Includes fields for full name, flat number, optional contact number, and mandatory biometric consent. Supports live camera capture with real-time feedback on face detection, resolution, and image sharpness, as well as an automated duplicate-face detection check.

### 4. Resident Directory and Management
A searchable resident directory with both tabular and visual card views. Administrators can search by name or flat number, inspect stored reference photos, update profile information, upload replacement photographs, and toggle access status between Active and Inactive.

### 5. Forensic Entry History
A complete, searchable audit log of every gate event. Supports filtering by date ranges, decision outcomes, or text search. Allows security supervisors to export filtered logs to a standard CSV file for external reporting.

### 6. Benchmark Analytics
An academic performance evaluation dashboard. Evaluates model accuracy, False Acceptance Rate (FAR), False Rejection Rate (FRR), precision, and recall against an isolated 150-probe test dataset. Includes an interactive Confusion Matrix and distance distribution histogram, along with one-click export for the formal markdown accuracy report.

---

## 5. Technology Stack

| Component | Technology | Version | Purpose |
|---|---|---|---|
| Programming Language | Python | 3.10 / 3.12 | Core application logic |
| User Interface | Streamlit | 1.67.0 | Multi-page dashboard and control room interface |
| Computer Vision | OpenCV | 5.0.0 | Frame capture, face detection, and image processing |
| Deep Learning | DeepFace / FaceNet | 0.0.105 | 512-dimensional facial embedding generation |
| Database Engine | SQLite (Python stdlib) | Built-in | Relational storage for profiles, logs, and encodings |
| Vector Computation | NumPy | 2.5.4 | Cosine distance and vector normalizations |
| Data Processing | Pandas | 3.1.1 | Table management and metric aggregations |
| Columnar Serialization | PyArrow | 19.0.1 | Efficient table data serialization |
| Data Visualization | Plotly | 7.1.0 | Interactive charts and confusion matrix heatmaps |
| Password Security | Bcrypt | 5.0.0 | Cryptographic password hashing for admin credentials |
| Automated Testing | Pytest | 9.2.0 | Unit, integration, and scenario testing |

---

## 6. Project Structure

```
smart-society-security/
|-- app.py                      # Main application entry point and router
|-- requirements.txt            # Pinned project dependencies
|-- .gitignore                  # Git exclusion rules for private data and models
|-- config/
|   `-- settings.py             # Global constants, thresholds, and camera configs
|-- database/
|   |-- db.py                   # SQLite connection manager and context handlers
|   |-- schema.sql              # Database schema definitions and indexes
|   |-- seed_data.py            # Baseline initialization script
|   `-- cleanup_residents.py    # Database maintenance and pruning utility
|-- modules/
|   |-- webcam.py               # Camera capture abstraction and resource cleanup
|   |-- face_detector.py        # OpenCV Haar Cascade detector and blur checks
|   |-- face_recognition.py     # Embedding model wrapper and distance calculations
|   |-- resident_manager.py     # Resident profile CRUD and duplicate checks
|   |-- access_controller.py    # Three-tier threshold decision engine
|   |-- entry_logger.py         # Rate-limited audit logging service
|   |-- report_generator.py     # Biometric benchmark metrics calculator
|   `-- ui_theme.py             # Custom styling and sidebar layout injector
|-- pages/
|   |-- 1_Dashboard.py          # Daily operations summary and telemetry
|   |-- 2_Live_Monitoring.py    # Live video stream and decision cards
|   |-- 3_Register_Resident.py  # Resident onboarding and biometric capture
|   |-- 4_Manage_Residents.py   # Resident directory and profile management
|   |-- 5_Entry_History.py      # Searchable forensic audit logs with CSV export
|   `-- 6_Analytics.py          # Academic benchmark evaluation and metrics
|-- models/
|   `-- haarcascade_frontalface_default.xml  # Bundled OpenCV face detector model
|-- data/
|   |-- residents/              # Stored resident profile photographs (gitignored)
|   `-- snapshots/              # Incident audit snapshots (gitignored)
|-- tests/
|   |-- conftest.py             # Shared fixtures and mock vectors
|   |-- test_access_controller.py  # Decision logic and threshold boundary tests
|   |-- test_database.py        # Database CRUD, constraints, and trigger tests
|   |-- test_recognition.py     # Vector normalization and distance tests
|   `-- test_reports.py         # Evaluation metrics and zero-division safeguard tests
`-- reports/
    `-- accuracy_report.md      # Exported formal academic benchmark report
```

---

## 7. Installation and Setup

### Prerequisites
- A laptop or desktop running Windows 10 or Windows 11.
- Python 3.10 or higher installed with PATH configured.
- A functional built-in or USB webcam.

### Step 1: Open the Project Directory
Open PowerShell or your command prompt and navigate to the project folder:
```powershell
cd "D:\Face Recognition System"
```

### Step 2: Install Dependencies
Install all required libraries using pip:
```powershell
python -m pip install -r requirements.txt
```

### Step 3: Initialize the Database
Run the seed script to create database tables, initialize default administrator credentials, and register baseline resident profiles:
```powershell
python database/seed_data.py
```

---

## 8. Running the Application

To start the local web application:
```powershell
python -m streamlit run app.py
```

The system will start the local server and automatically open the application in your default web browser at:
`http://localhost:8501`

### Default Login Credentials
- **Username:** `admin`
- **Password:** `admin123`

---

## 9. Automated Testing

The project includes an automated test suite covering vector normalization, database transactions, decision boundaries, and report generation.

Run all tests from the project root:
```powershell
python -m pytest tests/ -v
```

### Test Results Summary
All 17 automated tests pass deterministically:
```
tests/test_access_controller.py::test_evaluate_face_confident_match PASSED
tests/test_access_controller.py::test_evaluate_face_stranger_rejected PASSED
tests/test_access_controller.py::test_evaluate_face_none_probe PASSED
tests/test_access_controller.py::test_evaluate_face_empty_residents PASSED
tests/test_database.py::test_init_db_creates_tables PASSED
tests/test_database.py::test_register_and_retrieve_resident PASSED
tests/test_database.py::test_duplicate_resident_detection PASSED
tests/test_database.py::test_deactivate_resident PASSED
tests/test_database.py::test_update_resident_metadata PASSED
tests/test_recognition.py::test_embedding_shape_and_type PASSED
tests/test_recognition.py::test_embedding_l2_normalization PASSED
tests/test_recognition.py::test_cosine_distance_identical_vectors PASSED
tests/test_recognition.py::test_cosine_distance_orthogonal_vectors PASSED
tests/test_recognition.py::test_empty_face_raises_value_error PASSED
tests/test_reports.py::test_metrics_calculation_standard_case PASSED
tests/test_reports.py::test_metrics_zero_division_guard PASSED
tests/test_reports.py::test_export_markdown_report PASSED
============================= 17 passed in 2.77s ==============================
```

---

## 10. Performance and Evaluation Results

The recognition model was evaluated on an isolated test corpus of 150 verification probes (100 resident probes and 50 unknown stranger probes):

| Evaluation Metric | Measured Result | Project Target | Result Status |
|---|---|---|---|
| Overall Accuracy | 97.33% | >= 95.0% | Achieved |
| False Acceptance Rate (FAR) | 0.00% | <= 0.5% | Achieved (Zero unauthorized admissions) |
| False Rejection Rate (FRR) | 4.00% | <= 5.0% | Achieved (4 difficult probes routed to review) |
| Precision | 100.00% | >= 95.0% | Perfect Precision |
| Recall / Sensitivity | 96.00% | >= 95.0% | Achieved |
| Average Latency | 92.4 ms | < 2500 ms | Real-time Performance |

### Confusion Matrix Breakdown
- **True Positives (TP = 96):** Authorized residents correctly identified and permitted entry.
- **True Negatives (TN = 50):** Unregistered strangers correctly blocked at the entrance.
- **False Positives (FP = 0):** Zero security breaches where an impostor was wrongly admitted.
- **False Negatives (FN = 4):** Genuine resident attempts sent for manual check due to poor lighting or blur.

---

## 11. Security and Privacy Standards

- **Offline Operation:** The entire application runs locally on the host machine. Biometric data and video frames are never transmitted over the internet or to external cloud servers.
- **Password Protection:** Administrator passwords are never stored in plain text; they are secured using the industry-standard Bcrypt hashing algorithm.
- **Database Hygiene:** SQL queries use strict parameterization to prevent injection vulnerabilities. Biometric embeddings are stored as serialized binary blobs.
- **Biometric Consent:** The enrollment workflow includes an explicit consent confirmation requirement in compliance with privacy practices.
