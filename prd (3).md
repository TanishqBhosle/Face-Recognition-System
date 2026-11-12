# Product Requirements Document (PRD)

# Smart Society Security System

## AI-Based Face Recognition and Access Management

  -----------------------------------------------------------------------
  Field                               Details
  ----------------------------------- -----------------------------------
  Project type                        Academic assignment / working
                                      prototype

  Version                             1.0

  Status                              Implementation-ready

  Primary platform                    Windows laptop

  Primary language                    Python

  Core technologies                   OpenCV, FaceNet-compatible
                                      embeddings, SQLite, Streamlit
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 1. Project Overview

### 1.1 Vision

Build an intelligent, computer-vision-based security application that
assists security personnel in identifying registered residents at a
residential society entrance using a laptop webcam.

The application captures a live video stream, detects faces, compares
them against a database of registered residents, and displays a clear
recognition decision. It also manages resident profiles, records entry
attempts, and reports recognition performance.

### 1.2 Problem Statement

Traditional residential society security often depends on manual
identity verification. This can cause delays, inconsistent checks, human
error, and difficulty maintaining reliable entry records.

The proposed system uses face recognition to assist security personnel
with resident identification, unknown-person flagging, and digital
access logging.

### 1.3 Proposed Solution

Develop a local Python application with: - Live laptop webcam
monitoring. - Face detection and facial embedding generation. - Matching
against registered resident profiles. - Colour-coded recognition
outcomes. - Resident registration and management. - Timestamped
entry-attempt logs. - Accuracy and error-rate reporting.

**Important:** This is an identification-assistance prototype. A face
match alone must not physically unlock a gate or replace security guard
judgement.

------------------------------------------------------------------------

## 2. Goals and Success Criteria

### 2.1 Goals

1.  Integrate the laptop webcam for live video capture.
2.  Register at least 20 residents with consent.
3.  Detect faces and compare them against registered facial embeddings.
4.  Display green, red, or yellow recognition outcomes.
5.  Store resident profiles and entry attempts in SQLite.
6.  Provide a dashboard for monitoring and administration.
7.  Measure false acceptance and false rejection using a labelled test
    dataset.
8.  Deliver setup instructions, source code, test results, and a
    demonstration.

### 2.2 Success Criteria

The project is successful when: - The application launches on the target
Windows laptop. - The webcam feed can be started and stopped. - Faces
are detected in the live feed. - At least 20 residents can be
enrolled. - Registered and unknown test identities are evaluated
correctly according to the configured threshold. - Uncertain cases are
sent for manual verification. - Recognition attempts are logged without
excessive duplicate records. - The final report contains measured
metrics from a separate test set.

------------------------------------------------------------------------

## 3. Users and Roles

  -----------------------------------------------------------------------
  User                                Responsibilities
  ----------------------------------- -----------------------------------
  Security Guard                      Monitor the camera, review
                                      recognition outcomes, manually
                                      verify uncertain cases, and view
                                      entry history

  Administrator                       Register residents, update or
                                      deactivate profiles, manage access
                                      to records, and view reports

  Resident                            Provide an authorised photograph
                                      and consent to biometric
                                      registration
  -----------------------------------------------------------------------

The primary user is the security guard operating the entrance monitoring
station.

------------------------------------------------------------------------

## 4. Scope

### 4.1 In Scope --- Version 1

-   Local laptop webcam integration.
-   Face detection and recognition.
-   Registration of at least 20 residents.
-   Resident profile management.
-   Green / red / yellow recognition status.
-   Manual verification workflow.
-   SQLite resident and entry-log database.
-   Dashboard and live monitoring screen.
-   Searchable entry history.
-   Basic analytics and accuracy report.
-   Functional tests and project documentation.

### 4.2 Out of Scope --- Version 1

-   Automatic physical gate unlocking.
-   Production-grade multi-camera deployment.
-   Cloud-hosted biometric processing.
-   Mobile applications.
-   SMS or WhatsApp notifications.
-   Full visitor-management workflows.
-   Guaranteed spoof-proof or liveness detection.

These may be considered future enhancements.

------------------------------------------------------------------------

## 5. Functional Requirements

### FR-01: Live Webcam Monitoring

The system shall: - Access the laptop's built-in webcam. - Display a
live video stream. - Detect faces in each processed frame. - Draw
bounding boxes around detected faces. - Display camera connection
status. - Allow the operator to start and stop monitoring. - Handle
camera permission errors and disconnections gracefully.

**Acceptance criteria** - The webcam feed starts when a supported camera
is available. - A visible face can be detected under supported lighting
conditions. - Multiple faces can be detected in one frame. - If the
camera is unavailable, a clear error is shown and no recognition
approval is issued.

### FR-02: Resident Registration

Administrators shall be able to register a resident with:

  Field                    Requirement
  ------------------------ ------------------------------------
  Resident ID              System-generated unique identifier
  Full name                Required
  Flat number              Required
  Contact number           Optional
  Profile photograph       Required
  Face embedding           Generated by the recognition model
  Status                   Active or inactive
  Registration timestamp   Automatically generated

Registration workflow: 1. Enter resident details. 2. Capture a
photograph through the webcam or upload an image. 3. Validate that a
usable face is present. 4. Generate a facial embedding. 5. Save the
profile and embedding. 6. Display registration success or a clear
validation error.

The system should flag possible duplicate resident records for
administrator review.

**Acceptance criteria** - At least 20 resident profiles can be
created. - Each active resident has a valid facial embedding. -
Registration fails safely if no usable face is detected. -
Administrators can update or deactivate a profile.

### FR-03: Face Recognition Engine

The system shall compare a detected face with stored resident
embeddings.

Recognition workflow: 1. Capture a webcam frame. 2. Detect the face. 3.
Validate image quality and face location. 4. Generate an embedding using
a pretrained recognition model. 5. Compare it with active resident
embeddings. 6. Find the best candidate match. 7. Apply calibrated
acceptance and review thresholds. 8. Return a decision and supporting
match information.

Recommended implementation: - OpenCV for webcam capture and image
processing. - A compatible pretrained FaceNet model or another
documented face-embedding model. - Euclidean distance or cosine distance
for matching. - SQLite for resident and embedding storage.

The model and threshold must be selected and calibrated using validation
data. Thresholds are model-specific and must not be guessed or copied
from an unrelated model.

**Acceptance criteria** - Registered test identities can be matched
under supported conditions. - Unknown identities are not automatically
assigned to the nearest resident. - Low-quality or ambiguous matches are
sent for manual review. - Inactive profiles cannot receive an automatic
positive recognition decision.

### FR-04: Entry Decision System

The application shall show three decision states:

  -----------------------------------------------------------------------
  State                   Colour                  Meaning
  ----------------------- ----------------------- -----------------------
  ENTRY ALLOWED           Green                   A sufficiently
                                                  confident match to an
                                                  active registered
                                                  resident

  ENTRY REJECTED          Red                     No sufficiently close
                                                  match to an active
                                                  registered resident

  VERIFICATION REQUIRED   Yellow                  Ambiguous match, poor
                                                  image quality, or
                                                  another condition
                                                  requiring human review
  -----------------------------------------------------------------------

Decision rules: - A valid match within the calibrated acceptance
threshold may show green. - A match outside the review range may show
red as unrecognised. - A borderline match must show yellow. - No face,
multiple ambiguous faces, poor image quality, or system failure must
never result in automatic approval. - The security guard remains
responsible for the actual entry decision.

### FR-05: Entry Logging

Every completed recognition attempt shall be recorded.

Suggested fields: - Log ID. - Timestamp. - Resident ID, nullable for
unknown individuals. - Recognition distance or similarity score. -
Decision status. - Decision reason. - Optional snapshot reference,
subject to consent and retention policy.

The system shall: - Record recognised, rejected, and review-required
attempts. - Prevent repeated logs from every video frame through a
configurable cooldown or event-based logging rule. - Preserve an audit
trail. - Avoid silently changing historical records through ordinary
operator actions.

### FR-06: Resident Management

Administrators shall be able to: - View all resident records. - Search
by name or flat number. - Edit resident information. - Replace a profile
photograph and regenerate the embedding. - Activate or deactivate a
resident. - Delete biometric data and profile information when
authorised and required.

Deactivated residents must not be eligible for automatic recognition
approval.

### FR-07: Entry History

The application shall provide: - Recent entry attempts. - Date and
time. - Resident name and flat number when identified. - Decision
status. - Search and date filters. - Resident and status filters. -
Unknown-person records.

### FR-08: Analytics and Reports

The system shall report: - Total test attempts. - Correct
registered-person identifications. - Correct unknown-person
rejections. - False positives. - False negatives. - Precision. -
Recall. - False Acceptance Rate (FAR). - False Rejection Rate (FRR). -
Average processing time.

The report must be calculated from a labelled test dataset. Live
dashboard counts must not be presented as model accuracy.

------------------------------------------------------------------------

## 6. User Interface Requirements

The application should provide the following screens:

### Screen 1 --- Dashboard

-   Total registered residents.
-   Today's entry attempts.
-   Recognised attempts.
-   Rejected attempts.
-   Verification-required attempts.
-   Camera status.
-   Recent activity.

### Screen 2 --- Live Monitoring

-   Live webcam feed.
-   Face bounding boxes.
-   Recognition status and colour.
-   Resident name and flat number when identified.
-   Match distance or score, clearly labelled.
-   Start / stop camera controls.
-   Manual verification controls.

### Screen 3 --- Register Resident

-   Full name.
-   Flat number.
-   Optional contact number.
-   Webcam capture or image upload.
-   Face validation result.
-   Register button and confirmation.

### Screen 4 --- Manage Residents

-   Resident table.
-   Search by name or flat.
-   Edit profile.
-   Replace photograph.
-   Activate / deactivate.
-   Authorised deletion.

### Screen 5 --- Entry History

-   Timestamped log table.
-   Search and filters.
-   Decision status.
-   Resident details where available.
-   Rejection or review reason.

### Screen 6 --- Reports and Analytics

-   Confusion-matrix counts.
-   Accuracy, precision, recall, FAR, and FRR.
-   Performance by lighting condition.
-   Average processing time.
-   Exportable report.

------------------------------------------------------------------------

## 7. Technical Architecture

### 7.1 Architecture Overview

The application shall use a modular architecture:

1.  **Presentation layer:** Streamlit pages, dashboard, camera preview,
    and controls.
2.  **Application layer:** Resident management, access decision rules,
    logging, and reporting.
3.  **Computer-vision layer:** OpenCV capture, face detection,
    preprocessing, and embedding generation.
4.  **Recognition layer:** Embedding comparison, threshold evaluation,
    and match result.
5.  **Data layer:** SQLite database and protected local image/model
    storage.

### 7.2 Recommended Technology Stack

  -----------------------------------------------------------------------
  Layer                   Technology              Purpose
  ----------------------- ----------------------- -----------------------
  Programming language    Python 3.10 or          Main application
                          compatible version      

  User interface          Streamlit               Dashboard and screens

  Webcam and vision       OpenCV                  Capture and image
                                                  processing

  Face embeddings         FaceNet-compatible      Facial representation
                          pretrained model        

  Numerical processing    NumPy                   Embedding comparison

  Image handling          Pillow                  Image loading and
                                                  validation

  Database                SQLite                  Resident and entry data

  Reporting               Pandas                  Test-result analysis

  Charts                  Plotly                  Dashboard charts

  Testing                 Pytest                  Automated tests
  -----------------------------------------------------------------------

Pin and test compatible package versions in `requirements.txt`. The
chosen face-recognition library and pretrained model must be documented,
including setup and licensing requirements.

------------------------------------------------------------------------

## 8. Database Design

### 8.1 Residents Table

  Column           Type                  Description
  ---------------- --------------------- -----------------------------
  resident_id      INTEGER PRIMARY KEY   Unique resident identifier
  full_name        TEXT                  Resident name
  flat_number      TEXT                  Society flat identifier
  contact_number   TEXT                  Optional contact
  image_path       TEXT                  Profile photograph location
  face_encoding    BLOB                  Stored facial embedding
  status           TEXT                  Active / inactive
  created_at       DATETIME              Registration timestamp
  updated_at       DATETIME              Last update timestamp

### 8.2 Entry Logs Table

  Column           Type                  Description
  ---------------- --------------------- -----------------------------
  log_id           INTEGER PRIMARY KEY   Unique log identifier
  resident_id      INTEGER, nullable     Matched resident
  timestamp        DATETIME              Recognition time
  match_distance   REAL                  Model distance
  decision         TEXT                  Allowed / rejected / review
  reason           TEXT                  Decision explanation
  snapshot_path    TEXT, nullable        Optional snapshot reference

### 8.3 Admins Table

  Column          Type                  Description
  --------------- --------------------- --------------------------
  admin_id        INTEGER PRIMARY KEY   Unique administrator
  username        TEXT UNIQUE           Login name
  password_hash   TEXT                  Secure password hash
  role            TEXT                  Administrator / operator

### 8.4 Database Rules

-   Resident IDs must be unique.
-   Entry logs must support unknown individuals with a null resident ID.
-   Passwords must never be stored in plain text.
-   Only authorised administrators may manage resident biometric data.
-   Timestamps must use a consistent format.
-   Deletion and retention policies must cover photographs, embeddings,
    and snapshots.

------------------------------------------------------------------------

## 9. Recognition and Decision Logic

Illustrative decision flow:

``` python
def decide_entry(face_embedding, residents):
    if face_embedding is None:
        return "VERIFICATION_REQUIRED"

    if not residents:
        return "ENTRY_REJECTED"

    match = find_best_match(face_embedding, residents)

    if match is None:
        return "ENTRY_REJECTED"

    if match.distance <= ACCEPT_THRESHOLD:
        return "ENTRY_ALLOWED"

    if match.distance <= REVIEW_THRESHOLD:
        return "VERIFICATION_REQUIRED"

    return "ENTRY_REJECTED"
```

This is illustrative pseudocode. The matching function, threshold
direction, and threshold values must correspond to the selected model.

Additional safeguards: - Do not approve when no face is detected. - Do
not approve when multiple faces create an ambiguous match. - Do not
approve inactive resident profiles. - Do not reuse stale recognition
results. - Require consistent observations across multiple frames. -
Apply cooldowns to avoid duplicate logs. - Keep manual verification
available. - A recognition decision must not directly operate a physical
gate.

### 9.1 Basic Anti-Spoofing

A printed photograph or a photograph displayed on a mobile screen may
fool a basic recognition system.

For the academic prototype, optional basic checks may include: - Blink
detection. - Head movement checks. - Consecutive-frame consistency.

These are not reliable proof of liveness. Production deployment would
require a properly evaluated presentation-attack detection solution.

------------------------------------------------------------------------

## 10. Non-Functional Requirements

  -----------------------------------------------------------------------
  Requirement                         Target
  ----------------------------------- -----------------------------------
  Performance                         Target a recognition decision
                                      within 2--3 seconds under normal
                                      test conditions

  Reliability                         Handle webcam disconnections
                                      without crashing

  Usability                           Simple interface for security
                                      personnel

  Capacity                            At least 20 registered residents

  Maintainability                     Modular, documented Python code

  Security                            Restrict access to resident and
                                      biometric information

  Availability                        Local operation without mandatory
                                      internet access after setup

  Compatibility                       Windows 10/11 laptop

  Accuracy                            Measured on a separate labelled
                                      test set
  -----------------------------------------------------------------------

Performance targets are goals to validate, not claims of achieved
performance.

------------------------------------------------------------------------

## 11. Testing Strategy

### 11.1 Suggested Test Dataset

  Dataset                                  Quantity
  -------------------------------------- ----------
  Registered residents                           20
  Registration images per resident             3--5
  Separate test attempts per resident             5
  Unknown-person test identities                 10
  Unknown-person attempts per identity            5

This provides 100 registered-person attempts and 50 unknown-person
attempts.

Registration and test images must be separate. Where possible, test
variations in lighting, distance, head pose, and image quality. Avoid
treating consecutive frames from one video as independent test samples.

### 11.2 Functional Test Cases

  -----------------------------------------------------------------------
  Test ID                 Scenario                Expected Result
  ----------------------- ----------------------- -----------------------
  TC-01                   Registered resident     Green result when match
                                                  meets calibrated
                                                  threshold

  TC-02                   Unknown person          Red result when no
                                                  match is sufficiently
                                                  close

  TC-03                   Borderline match        Yellow manual
                                                  verification

  TC-04                   No face in frame        No automatic approval

  TC-05                   Multiple faces          Detect separately;
                                                  ambiguous cases require
                                                  review

  TC-06                   Inactive resident       No automatic approval

  TC-07                   Webcam disconnected     Camera error shown

  TC-08                   Duplicate registration  Warning or
                                                  administrator review

  TC-09                   Recognition completed   Entry log created

  TC-10                   Search resident         Correct profile
                                                  displayed

  TC-11                   Filter history          Correct records
                                                  displayed

  TC-12                   Update resident photo   New embedding generated
  -----------------------------------------------------------------------

### 11.3 Evaluation Metrics

Let: - TP = True Positives. - TN = True Negatives. - FP = False
Positives. - FN = False Negatives.

**Accuracy**

`(TP + TN) / (TP + TN + FP + FN) × 100`

**False Acceptance Rate (FAR)**

`FP / (FP + TN) × 100`

**False Rejection Rate (FRR)**

`FN / (FN + TP) × 100`

**Precision**

`TP / (TP + FP) × 100`

**Recall**

`TP / (TP + FN) × 100`

For this project, false acceptance is a particularly important security
error. Accuracy alone is insufficient. Report the sample counts and test
conditions alongside all metrics. If a denominator is zero, report the
metric as not applicable rather than inventing a value.

The final report must contain actual measured results, not assumed
accuracy percentages.

------------------------------------------------------------------------

## 12. Privacy and Security Requirements

The system processes biometric information and must handle it carefully.

Requirements: 1. Obtain informed consent before enrolling residents. 2.
Use consented volunteers or appropriately authorised images for testing.
3. Restrict resident registration and deletion to authorised
administrators. 4. Protect facial embeddings and profile photographs. 5.
Avoid unnecessary video recording. 6. Define data retention and deletion
policies. 7. Hash administrator passwords using a suitable
password-hashing algorithm. 8. Prevent unauthorised access to resident
records. 9. Provide a manual identity-verification alternative. 10. Do
not expose facial data in public dashboard views. 11. Do not physically
unlock an entrance solely because of a face match.

------------------------------------------------------------------------

## 13. Recommended Project Folder Structure

``` text
smart-society-security/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── config/
│   └── settings.py
│
├── database/
│   ├── db.py
│   └── schema.sql
│
├── modules/
│   ├── webcam.py
│   ├── face_detector.py
│   ├── face_recognition.py
│   ├── resident_manager.py
│   ├── access_controller.py
│   ├── entry_logger.py
│   └── report_generator.py
│
├── pages/
│   ├── dashboard.py
│   ├── live_monitoring.py
│   ├── register_resident.py
│   ├── manage_residents.py
│   ├── entry_history.py
│   └── analytics.py
│
├── models/
│   └── README.md
│
├── data/
│   ├── residents/
│   └── snapshots/
│
├── tests/
│   ├── test_recognition.py
│   ├── test_database.py
│   ├── test_access_controller.py
│   └── test_reports.py
│
└── reports/
    └── accuracy_report.md
```

Private photographs, embeddings, database files, model weights, and
secrets must not be committed to a public Git repository. Model files
should be downloaded separately where required.

------------------------------------------------------------------------

## 14. Development Roadmap

Suggested seven-day implementation schedule:

  -----------------------------------------------------------------------
  Day                     Tasks                   Expected outcome
  ----------------------- ----------------------- -----------------------
  Day 1                   Environment setup,      Working webcam feed
                          OpenCV, webcam          

  Day 2                   Face detection and      Face-processing module
                          embedding generation    

  Day 3                   Resident registration   At least 20 registered
                          and SQLite              residents

  Day 4                   Recognition and         Green / red / yellow
                          decision engine         outcomes

  Day 5                   Streamlit dashboard and Functional application
                          entry logs              

  Day 6                   Analytics and accuracy  Measured test results
                          testing                 

  Day 7                   Bug fixes,              Final submission
                          documentation, demo     
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 15. Deliverables

  Deliverable                Description
  -------------------------- ----------------------------------------------
  Working application        Python-based face recognition prototype
  Webcam integration         Live laptop webcam feed
  Resident database          At least 20 consented registered faces
  Recognition engine         Face detection and embedding matching
  Entry decision interface   Green, red, and yellow status
  SQLite database            Resident profiles and entry logs
  Dashboard                  Monitoring and administration screens
  Test report                Accuracy, FAR, FRR, precision, and recall
  Documentation              Installation, configuration, and usage guide
  Demonstration              Live working prototype

------------------------------------------------------------------------

## 16. Definition of Done

-   [ ] Application launches successfully on Windows.
-   [ ] Laptop webcam works inside the application.
-   [ ] Face detection works in the live feed.
-   [ ] At least 20 residents are registered.
-   [ ] Registered test identities can be evaluated.
-   [ ] Unknown individuals are flagged.
-   [ ] Green, red, and yellow outcomes work.
-   [ ] Entry attempts are stored in SQLite.
-   [ ] Resident management works.
-   [ ] Entry history and filters work.
-   [ ] Analytics and evaluation metrics are generated.
-   [ ] Functional test cases are executed.
-   [ ] Accuracy and error rates are calculated from actual test data.
-   [ ] Privacy and security safeguards are documented.
-   [ ] Final README and demonstration are ready.

------------------------------------------------------------------------

## 17. Risks and Mitigation

  -----------------------------------------------------------------------
  Risk                                Mitigation
  ----------------------------------- -----------------------------------
  Poor lighting                       Test multiple lighting conditions
                                      and improve image quality

  Face angle variation                Enrol multiple authorised
                                      photographs

  False recognition                   Calibrate thresholds and require
                                      consistent matches

  Webcam failure                      Show camera error and allow retry

  Photograph spoofing                 Add liveness checks and manual
                                      verification

  Duplicate records                   Flag possible duplicates during
                                      registration

  Slow processing                     Resize frames and process selected
                                      frames

  Data leakage                        Protect biometric data and restrict
                                      access

  Model installation issues           Pin compatible dependencies and
                                      document setup
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 18. Future Enhancements

Potential future features: - RFID or QR-based alternative
verification. - Visitor registration and approval. - Notifications to
residents. - Multiple entrance camera support. - Cloud-based society
management. - Mobile application for administrators. - Integration with
physical access-control hardware. - Advanced presentation-attack
detection.

These features are outside Version 1 scope.

------------------------------------------------------------------------

## 19. Final Product Summary

**Smart Society Security System** is a local AI-powered face-recognition
and security-monitoring prototype. It combines webcam-based face
detection, facial embeddings, resident registration, access-decision
assistance, SQLite logging, and recognition-performance reporting.

The project will be evaluated on: - Working webcam integration. -
Reliable resident enrolment and matching. - Safe handling of unknown and
uncertain identities. - Clear entry status presentation. - Accurate and
traceable entry logs. - Honest measurement of recognition performance. -
Usability, documentation, and demonstration quality.

**Recommended implementation stack:** Python, OpenCV, a pretrained
FaceNet-compatible embedding model, SQLite, Streamlit, NumPy, Pandas,
and Pytest.
