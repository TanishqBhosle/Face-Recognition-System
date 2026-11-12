import sys
import time
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import cv2
import numpy as np
from PIL import Image

from modules.webcam import WebcamCapture
from modules.face_detector import FaceDetector
from modules.face_recognition import EmbeddingModel
from modules.access_controller import AccessController, DecisionEnum
from modules.resident_manager import ResidentManager
from modules.entry_logger import EntryLogger
from modules.ui_theme import inject_custom_css, render_sidebar
from config.settings import ACCEPT_THRESHOLD, REVIEW_THRESHOLD

st.set_page_config(page_title="Live Monitoring | Smart Society Security", page_icon="📹", layout="wide")

inject_custom_css()
render_sidebar()

# Header
st.markdown(
    """
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
        <div>
            <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; color: #F8FAFC;">📹 Live Entrance Monitoring Station</h1>
            <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.95rem;">Real-time AI facial recognition and access verification aiding security personnel.</p>
        </div>
        <div style="text-align: right;">
            <span class="badge-pill badge-blue">THRESHOLD: ACCEPT &le; 0.40 | REVIEW &le; 0.55</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_resource
def get_services():
    detector = FaceDetector()
    embedder = EmbeddingModel.get_instance()
    controller = AccessController(accept_threshold=ACCEPT_THRESHOLD, review_threshold=REVIEW_THRESHOLD)
    res_mgr = ResidentManager()
    logger = EntryLogger()
    return detector, embedder, controller, res_mgr, logger

detector, embedder, controller, res_mgr, logger = get_services()

if "monitoring_active" not in st.session_state:
    st.session_state.monitoring_active = False
if "last_result" not in st.session_state:
    st.session_state.last_result = None

active_residents = res_mgr.get_all_active_residents()

# Top Controls Bar
col_ctrl1, col_ctrl2 = st.columns([1, 2], gap="medium")
with col_ctrl1:
    if not st.session_state.monitoring_active:
        if st.button("▶️ Activate Live Camera Feed", type="primary", width="stretch"):
            st.session_state.monitoring_active = True
            st.rerun()
    else:
        if st.button("⏹️ Pause Video Feed", type="secondary", width="stretch"):
            st.session_state.monitoring_active = False
            st.rerun()

with col_ctrl2:
    mode_selection = st.radio(
        "Capture Mode",
        ["Live OpenCV Feed", "Instant Camera Snapshot", "Upload Probe Image"],
        horizontal=True,
        label_visibility="collapsed"
    )

st.markdown("<br>", unsafe_allow_html=True)

# Main Screen Split: Left (Camera Stream) | Right (Decision HUD)
col_feed, col_card = st.columns([3, 2], gap="large")

def process_frame(frame_rgb):
    faces = detector.detect_faces(frame_rgb)
    decision_result = None
    annotated_frame = frame_rgb.copy()

    if len(faces) == 0:
        decision_result = controller.evaluate_face(
            probe_embedding=None,
            active_residents=active_residents,
            quality_reason="No face detected in camera field."
        )
    elif len(faces) > 1:
        faces_data = [detector.assess_face_quality(frame_rgb, box) for box in faces]
        annotated_frame = detector.draw_overlays(frame_rgb, faces_data, primary_color=(245, 158, 11), label="MULTIPLE")
        decision_result = controller.evaluate_face(
            probe_embedding=None,
            active_residents=active_residents,
            quality_reason="Multiple individuals detected. Please approach one at a time."
        )
    else:
        quality = detector.assess_face_quality(frame_rgb, faces[0])
        if quality["is_blurred"]:
            annotated_frame = detector.draw_overlays(frame_rgb, [quality], primary_color=(245, 158, 11), label="BLURRY")
            decision_result = controller.evaluate_face(
                probe_embedding=None,
                active_residents=active_residents,
                quality_reason=f"Face is blurred (Score: {quality['blur_score']:.1f} < 80). Hold still."
            )
        else:
            try:
                embedding = embedder.generate_embedding(quality["face_crop"])
                decision_result = controller.evaluate_face(embedding, active_residents)
            except Exception as e:
                decision_result = controller.evaluate_face(
                    probe_embedding=None,
                    active_residents=active_residents,
                    quality_reason=f"Embedding error: {str(e)}"
                )

            box_color = (16, 185, 129) if decision_result.decision == DecisionEnum.ALLOWED else (
                (245, 158, 11) if decision_result.decision == DecisionEnum.VERIFY else (239, 68, 68)
            )
            label = decision_result.resident.full_name if decision_result.resident else "UNKNOWN"
            annotated_frame = detector.draw_overlays(frame_rgb, [quality], primary_color=box_color, label=label)

    if decision_result:
        res_id = decision_result.resident.resident_id if decision_result.resident else None
        logger.log_attempt(
            resident_id=res_id,
            match_distance=decision_result.distance,
            decision=decision_result.decision.value,
            reason=decision_result.reason
        )

    st.session_state.last_result = decision_result
    return annotated_frame

# Left Column: Stream Video HUD
with col_feed:
    st.markdown(
        """
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
            <span style="font-weight: 700; color: #F8FAFC; font-size: 1.05rem;">📹 Video Stream Monitor</span>
            <span class="badge-pill badge-green"><span class="status-dot dot-green"></span>CAM-01 • 640x480</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    video_placeholder = st.empty()

    if mode_selection == "Live OpenCV Feed":
        if st.session_state.monitoring_active:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                st.error("⚠️ Unable to access webcam at device index 0. Try 'Instant Camera Snapshot' below.")
                st.session_state.monitoring_active = False
            else:
                for _ in range(30):
                    ret, frame = cap.read()
                    if not ret or frame is None:
                        break
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    annotated = process_frame(frame_rgb)
                    video_placeholder.image(annotated, channels="RGB", width="stretch")
                    time.sleep(0.04)
                cap.release()
                if st.session_state.monitoring_active:
                    st.rerun()
        else:
            video_placeholder.markdown(
                """
                <div style="background: rgba(15, 23, 42, 0.85); border: 2px dashed rgba(255, 255, 255, 0.1); border-radius: 14px; padding: 60px 20px; text-align: center;">
                    <div style="font-size: 2.5rem; margin-bottom: 10px;">📹</div>
                    <h3 style="color: #F8FAFC; margin: 0 0 6px 0;">Camera Stream Paused</h3>
                    <p style="color: #94A3B8; margin: 0;">Click <b>"Activate Live Camera Feed"</b> to commence real-time surveillance.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    elif mode_selection == "Instant Camera Snapshot":
        camera_photo = st.camera_input("Capture instant verification probe")
        if camera_photo:
            img = Image.open(camera_photo).convert("RGB")
            frame_rgb = np.array(img)
            annotated = process_frame(frame_rgb)
            video_placeholder.image(annotated, channels="RGB", width="stretch")

    elif mode_selection == "Upload Probe Image":
        uploaded = st.file_uploader("Upload gate probe portrait", type=["jpg", "jpeg", "png"])
        if uploaded:
            img = Image.open(uploaded).convert("RGB")
            frame_rgb = np.array(img)
            annotated = process_frame(frame_rgb)
            video_placeholder.image(annotated, channels="RGB", width="stretch")

# Right Column: Decision Telemetry & Guard Actions
with col_card:
    st.markdown(
        """
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
            <span style="font-weight: 700; color: #F8FAFC; font-size: 1.05rem;">🛡️ Gate Decision HUD</span>
            <span class="badge-pill badge-blue">AI EVALUATOR</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    result = st.session_state.last_result

    if result is None:
        st.markdown(
            """
            <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 48px 24px; text-align: center; color: #94A3B8;">
                <div style="font-size: 2rem; margin-bottom: 8px;">⏱️</div>
                <h4 style="color: #F8FAFC; margin: 0 0 6px 0;">Standby Mode</h4>
                <p style="margin: 0; font-size: 0.88rem;">Awaiting subject in front of camera lens.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # High-Impact Status Banners
        if result.decision == DecisionEnum.ALLOWED:
            st.markdown(
                f"""
                <div class="hud-decision-allowed">
                    <div style="font-size: 2.2rem; line-height: 1; margin-bottom: 4px;">✅</div>
                    <div style="font-size: 1.8rem; font-weight: 800; letter-spacing: 0.02em; color: #FFFFFF;">ENTRY ALLOWED</div>
                    <div style="font-size: 0.95rem; color: #D1FAE5; margin-top: 4px; font-weight: 600;">Active Resident Confirmed</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        elif result.decision == DecisionEnum.VERIFY:
            st.markdown(
                f"""
                <div class="hud-decision-verify">
                    <div style="font-size: 2.2rem; line-height: 1; margin-bottom: 4px;">⚠️</div>
                    <div style="font-size: 1.8rem; font-weight: 800; letter-spacing: 0.02em; color: #FFFFFF;">VERIFY REQUIRED</div>
                    <div style="font-size: 0.95rem; color: #FEF3C7; margin-top: 4px; font-weight: 600;">Manual Guard Check Prompted</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="hud-decision-reject">
                    <div style="font-size: 2.2rem; line-height: 1; margin-bottom: 4px;">🛑</div>
                    <div style="font-size: 1.8rem; font-weight: 800; letter-spacing: 0.02em; color: #FFFFFF;">ENTRY REJECTED</div>
                    <div style="font-size: 0.95rem; color: #FEE2E2; margin-top: 4px; font-weight: 600;">Unregistered Individual / Intruder</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Matched Subject Profile Box
        if result.resident:
            st.markdown(
                f"""
                <div class="subject-badge">
                    <img src="{result.resident.image_path if Path(result.resident.image_path).exists() else 'https://via.placeholder.com/90'}" class="subject-avatar" />
                    <div style="flex: 1;">
                        <div style="font-size: 1.25rem; font-weight: 800; color: #F8FAFC; margin-bottom: 4px;">{result.resident.full_name}</div>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                            <span class="badge-pill badge-green">FLAT {result.resident.flat_number}</span>
                            <span class="badge-pill badge-blue">{result.resident.status}</span>
                        </div>
                        <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 6px;">📞 {result.resident.contact_number or 'No phone registered'}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 16px; text-align: center;">
                    <div style="font-size: 0.95rem; color: #F8FAFC; font-weight: 600;">No Registered Resident Matched</div>
                    <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 4px;">Subject is not in society resident database.</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Telemetry Metrics
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.metric("Cosine Distance", f"{result.distance:.3f}", help="Calculated vector distance (0.00 = identical, 1.00+ = stranger)")
        with col_t2:
            st.metric("Confidence Score", f"{result.confidence_score}%")

        st.info(f"**Diagnostic Note:** {result.reason}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Guard Action Overrides
        st.markdown("##### 🛡️ Guard Access Actions")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            if st.button("✅ Force Manual Admit", width="stretch", type="primary"):
                logger.log_attempt(
                    resident_id=result.resident.resident_id if result.resident else None,
                    match_distance=result.distance,
                    decision="ENTRY_ALLOWED",
                    reason="Guard Manual Override: Admitted after physical verification."
                )
                st.success("Entry permitted & logged.")
        with col_g2:
            if st.button("🛑 Force Deny Entry", width="stretch"):
                logger.log_attempt(
                    resident_id=result.resident.resident_id if result.resident else None,
                    match_distance=result.distance,
                    decision="ENTRY_REJECTED",
                    reason="Guard Manual Override: Denied entry at gate."
                )
                st.warning("Entry rejected & logged.")
