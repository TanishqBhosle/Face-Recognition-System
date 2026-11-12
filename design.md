# UI/UX Specification & Design System
# Smart Society Security System

---

## 1. Design System & Visual Language

The user interface of the Smart Society Security System is designed specifically for **security station operations** on a Windows laptop. It prioritizes **immediate glanceability from 2–3 meters away**, unambiguous high-contrast decision indicators, minimal cognitive load for security personnel, and rapid keyboard/mouse interactions.

### 1.1 Color Palette

| Semantic Role | Hex Code | Visual Swatch | Purpose |
|---|---|---|---|
| **Entry Allowed (Green)** | `#22C55E` / `#16A34A` | 🟢 Emerald Green | Confident match to active resident. Gate entry recommended. |
| **Verification Required (Yellow)** | `#F59E0B` / `#D97706` | 🟡 Amber Yellow | Ambiguous match, poor lighting, or blur. Manual check required. |
| **Entry Rejected (Red)** | `#EF4444` / `#DC2626` | 🔴 Crimson Red | Unregistered person / stranger. Access denied. |
| **Primary Brand Navy** | `#1E3A8A` / `#0F172A` | 🔵 Deep Navy Slate | Header bars, primary navigation, branding accents. |
| **Neutral Background (Dark Mode)**| `#0F172A` | ⬛ Dark Charcoal | Reduces eye fatigue during overnight guard shifts. |
| **Card / Surface Background** | `#1E293B` | 🔲 Slate Grey | Elevated cards, metric panels, video frame wrapper. |
| **Text Primary** | `#F8FAFC` | ⚪ Off-White | High-contrast readable typography for live video overlays. |
| **Text Secondary / Muted** | `#94A3B8` | 🔘 Slate Muted | Timestamps, metadata, labels, and secondary indicators. |

---

### 1.2 Typography & Sizing Hierarchy

- **Font Family**: Modern system sans-serif (`Inter`, `Segoe UI`, `-apple-system`, `Roboto`).
- **Live Status Outcome Banner**: `font-size: 2.25rem (36px)`, `font-weight: 800`, All Caps, high-contrast banner with 12px border-radius.
- **Metric Card Counters**: `font-size: 2.0rem (32px)`, `font-weight: 700`, bold tabular numerals.
- **Section Headers (H1/H2)**: `font-size: 1.5rem (24px)` to `1.25rem (20px)`, `font-weight: 600`.
- **Data Table & Logs**: `font-size: 0.875rem (14px)`, monospaced timestamp and distance figures for aligned tabular scanning.

---

## 2. Navigation & Application Layout

The application utilizes Streamlit’s native multi-page sidebar navigation (`pages/`), with persistent system status indicators and security session controls.

### 2.1 Sidebar Layout Specification
```
┌───────────────────────────────────────────┐
│ 🏢 SMART SOCIETY SECURITY                 │
│ Guard Post: Main Gate A                   │
├───────────────────────────────────────────┤
│ 📌 NAVIGATION                             │
│  [🏠] Dashboard                           │
│  [📹] Live Monitoring                     │
│  [➕] Register Resident                   │
│  [👥] Manage Residents                    │
│  [📜] Entry History                       │
│  [📊] Analytics & Reports                 │
├───────────────────────────────────────────┤
│ ⚙️ SYSTEM HEALTH                          │
│  Camera: 🟢 ONLINE (720p @ 30fps)         │
│  Active Residents: 24 Enrolled            │
│  Database: 🟢 CONNECTED                   │
├───────────────────────────────────────────┤
│ 👤 Guard: On Duty (Shift 1)   [🔒 Logout] │
└───────────────────────────────────────────┘
```

---

## 3. Screen-by-Screen UI/UX Specifications

### Screen 1: Dashboard (`pages/dashboard.py`)
Provides an executive overview of the security gate status, daily volume, and quick navigation.

```
┌────────────────────────────────────────────────────────────────────────┐
│  Dashboard Overview                                📅 Nov 12, 2026     │
├──────────────┬──────────────┬──────────────┬─────────────┬─────────────┤
│ Total Active │ Today's      │ Granted      │ Rejected    │ Manual      │
│ Residents    │ Attempts     │ (Green)      │ (Red)       │ Review (Yel)│
│    24        │     142      │     118      │     16      │      8      │
├──────────────┴──────────────┴──────────────┴─────────────┴─────────────┤
│ 📹 CAMERA QUICK-STATUS                                                  │
│  Status: [● OPERATIONAL]   |   FPS: 28.4   |   Latency: 142 ms          │
│  [ Open Live Monitoring Feed ] ->                                       │
├────────────────────────────────────────────────────────────────────────┤
│ 🕒 RECENT GATE ACTIVITY (LAST 5 EVENTS)                                │
│  • 20:41:12 - Rahul Sharma (Flat A-102) -> GRANTED (Dist: 0.28)        │
│  • 20:38:50 - Unknown Person -> REJECTED (Dist: 0.74)                  │
│  • 20:35:10 - Priya Patel (Flat C-304) -> GRANTED (Dist: 0.31)         │
│  • 20:31:05 - Unidentified Subject -> VERIFY (Dist: 0.49 - Blur)       │
│  • 20:25:40 - Amit Verma (Flat B-201) -> GRANTED (Dist: 0.22)          │
└────────────────────────────────────────────────────────────────────────┘
```

---

### Screen 2: Live Monitoring (`pages/live_monitoring.py`)
The primary operational screen for security guards during duty hours.

```
┌────────────────────────────────────────┬───────────────────────────────┐
│  LIVE CAMERA FEED                      │  RECOGNITION OUTCOME PANEL    │
│ ┌────────────────────────────────────┐ │ ┌───────────────────────────┐ │
│ │                                    │ │ │                           │ │
│ │        [ CAMERA FRAME ]            │ │ │       ENTRY ALLOWED       │ │
│ │                                    │ │ │          (GREEN)          │ │
│ │      ┌─────────────────┐           │ │ │                           │ │
│ │      │   DETECTED      │           │ │ └───────────────────────────┘ │
│ │      │     FACE        │           │ │ 👤 RESIDENT DETAILS           │
│ │      │  [Green Box]    │           │ │ Name: Rahul Sharma            │
│ │      └─────────────────┘           │ │ Flat: A-102                   │
│ │                                    │ │ Status: ACTIVE RESIDENT       │
│ │                                    │ │ Match Distance: 0.28          │
│ │ FPS: 28.5 | Res: 1280x720          │ │ Threshold: <= 0.40 (Confident)│
│ └────────────────────────────────────┘ │ ───────────────────────────── │
│ [ ⏹️ Stop Camera ] [ 🔄 Refresh Feed ]  │ 🛡️ GUARD ACTIONS             │
│                                        │ [ Grant Manual Entry ]        │
│                                        │ [ Deny Entry & Sound Alert ]  │
│                                        │ [ Log Incident Note ]         │
└────────────────────────────────────────┴───────────────────────────────┘
```

#### Visual Decision Card States:
1. **Green Card (`ENTRY_ALLOWED`)**:
   - Background: `#16A34A` with high-contrast white text.
   - Large tick icon `✓`.
   - Displays Resident Name, Flat Number, reference photograph thumbnail for visual confirmation.
2. **Yellow Card (`VERIFICATION_REQUIRED`)**:
   - Background: `#D97706` with bold black/white text.
   - Alert triangle `⚠`.
   - Text: *"Ambiguous Match (Dist: 0.48). Guard verification required."*
   - Prompts guard to inspect physical ID or ask flat number.
3. **Red Card (`ENTRY_REJECTED`)**:
   - Background: `#DC2626` with bold white text.
   - Stop hand `🛑` or cross `✖`.
   - Text: *"Unregistered Person (Dist: 0.76). Direct to visitor gate."*

---

### Screen 3: Register Resident (`pages/register_resident.py`)
Form screen for administrative enrolment of residents.

```
┌────────────────────────────────────────────────────────────────────────┐
│  Register New Resident Profile                                         │
├────────────────────────────────────────┬───────────────────────────────┤
│ 📝 RESIDENT INFORMATION                │ 📷 BIOMETRIC PHOTO ENROLMENT  │
│                                        │                               │
│ Full Name *                            │ Choose Capture Method:        │
│ [ e.g. Sunita Deshmukh              ]  │ (●) Live Webcam  ( ) Upload   │
│                                        │ ┌───────────────────────────┐ │
│ Flat Number *                          │ │                           │ │
│ [ e.g. D-501                        ]  │ │   [ WEBCAM CAPTURE ]      │ │
│                                        │ │                           │ │
│ Contact Number (Optional)              │ └───────────────────────────┘ │
│ [ +91 9876543210                    ]  │ [ 📸 Capture Photo ]          │
│                                        │                               │
│ Consent Agreement *                    │ Quality Checks:               │
│ [x] Resident signed biometric consent. │ Face Detected:  🟢 Pass (1)   │
│                                        │ Size (>80px):   🟢 Pass (180px│
│                                        │ Blur Score:     🟢 Pass (240) │
│                                        │ Duplicate Check:🟢 Clear      │
├────────────────────────────────────────┴───────────────────────────────┤
│ [ 💾 Complete Registration & Save Profile ]    [ ❌ Reset Form ]       │
└────────────────────────────────────────────────────────────────────────┘
```

---

### Screen 4: Manage Residents (`pages/manage_residents.py`)
Searchable data grid and CRUD management console.

```
┌────────────────────────────────────────────────────────────────────────┐
│  Resident Directory & Management                                       │
│                                                                        │
│  🔍 Search: [ Flat D-501 or Sunita      ]   Filter Status: [ All  ▼ ]  │
├──────┬──────────────────┬──────────┬─────────────┬──────────┬──────────┤
│ ID   │ Name             │ Flat     │ Contact     │ Status   │ Actions  │
├──────┼──────────────────┼──────────┼─────────────┼──────────┼──────────┤
│ 101  │ Rahul Sharma     │ A-102    │ 9820112233  │ ACTIVE   │ ✏️ 🔄 🚫 │
│ 102  │ Sunita Deshmukh  │ D-501    │ 9876543210  │ ACTIVE   │ ✏️ 🔄 🚫 │
│ 103  │ John Doe         │ B-104    │ -           │ INACTIVE │ ✏️ 🔄 ✅ │
└──────┴──────────────────┴──────────┴─────────────┴──────────┴──────────┘
 Actions: ✏️ Edit Details | 🔄 Update Face Photo | 🚫 Deactivate | ✅ Activate
```

---

### Screen 5: Entry History (`pages/entry_history.py`)
Forensic audit trail of all access events at the society gate.

```
┌────────────────────────────────────────────────────────────────────────┐
│  Entry History & Audit Logs                                            │
│                                                                        │
│  Date Range: [2026-11-01 to 2026-11-12]   Decision: [ All Decisions ▼] │
│  Search Query: [ Flat / Name           ]   [ Export to CSV ]           │
├──────────────┬──────────────────┬───────┬────────────┬───────┬─────────┤
│ Timestamp    │ Resident / Name  │ Flat  │ Decision   │ Dist  │ Reason  │
├──────────────┼──────────────────┼───────┼────────────┼───────┼─────────┤
│ 20:41:12     │ Rahul Sharma     │ A-102 │ 🟢 ALLOWED │ 0.28  │ Match OK│
│ 20:38:50     │ Unknown Subject  │ -     │ 🔴 REJECT  │ 0.74  │ No match│
│ 20:35:10     │ Priya Patel      │ C-304 │ 🟢 ALLOWED │ 0.31  │ Match OK│
│ 20:31:05     │ Unverified       │ -     │ 🟡 VERIFY  │ 0.49  │ Low Res │
└──────────────┴──────────────────┴───────┴────────────┴───────┴─────────┘
 Showing 1-4 of 1,248 entries. Page: [ 1 ] 2 3 4 ... 25
```

---

### Screen 6: Reports & Analytics (`pages/analytics.py`)
Academic evaluation report screen displaying confusion matrix, error rates, and chart visualizations.

```
┌────────────────────────────────────────────────────────────────────────┐
│  Model Benchmark & Recognition Accuracy Report                         │
│  Evaluation Dataset: 150 Labelled Probe Samples (100 Res, 50 Strangers)│
├──────────────┬──────────────┬──────────────┬─────────────┬─────────────┤
│ Accuracy     │ FAR (FMR)    │ FRR (FNMR)   │ Precision   │ Recall      │
│   97.33%     │    0.00%     │    4.00%     │   100.0%    │   96.00%    │
├──────────────┴──────────────┴──────────────┴─────────────┴─────────────┤
│ 📊 CONFUSION MATRIX                   │ 📈 DISTANCE DISTRIBUTION HIST  │
│                                       │                                │
│               Predicted:              │   Resident Pairs (Mean: 0.26)  │
│               Resident    Stranger    │   [█████████]                  │
│ Actual Res:   TP = 96     FN = 4      │                                │
│ Actual Str:   FP = 0      TN = 50     │   Impostor Pairs (Mean: 0.72)  │
│                                       │          [██████████████]      │
│ Zero False Acceptances achieved!      │   Threshold: | 0.40            │
├───────────────────────────────────────┴────────────────────────────────┤
│ 📥 [ Export Official Markdown Report ]    [ Re-run Evaluation Suite ]  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. State Management & Guard Usability Flow

### 4.1 Session State (`st.session_state`) Schema
- `st.session_state.is_authenticated`: Boolean indicating admin login.
- `st.session_state.camera_active`: Boolean tracking webcam capture thread.
- `st.session_state.last_decision`: Caches the latest `DecisionResult` DTO.
- `st.session_state.cooldown_tracker`: In-memory dictionary preventing frame-by-frame log spam.
- `st.session_state.active_residents_cache`: Cached list of enrolled resident vectors refreshed on CRUD events.

### 4.2 Guard Ergonomics Guidelines
- **Zero-Accident Design**: The "Grant Manual Entry" and "Deny Entry" buttons are separated with distinct color coding to prevent accidental mis-clicks.
- **Audio Feedback**: Subtle auditory chime on Green match; distinct alerting beep on Yellow/Red matches.
- **Single-Screen Shift Workflow**: A security guard can keep `pages/live_monitoring.py` open continuously throughout an 8-hour shift without needing to navigate away or manually refresh.

