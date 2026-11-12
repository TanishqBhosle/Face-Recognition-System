import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import numpy as np
from PIL import Image

from modules.face_detector import FaceDetector
from modules.face_recognition import EmbeddingModel
from modules.resident_manager import ResidentManager
from modules.ui_theme import inject_custom_css, render_sidebar

st.set_page_config(page_title="Register Resident | Smart Society Security", page_icon="➕", layout="wide")

inject_custom_css()
render_sidebar()

# Page Header
st.markdown(
    """
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
        <div>
            <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; color: #F8FAFC;">➕ Resident Biometric Onboarding</h1>
            <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.95rem;">Enrolling a new residential society member with facial embedding extraction.</p>
        </div>
        <div style="text-align: right;">
            <span class="badge-pill badge-green">MANDATORY CONSENT ENFORCED</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

res_mgr = ResidentManager()
detector = FaceDetector()
embedder = EmbeddingModel.get_instance()

col_form, col_photo = st.columns([1, 1], gap="large")

with col_form:
    st.markdown(
        """
        <div class="security-card">
            <h3 style="margin: 0 0 16px 0; font-size: 1.2rem; font-weight: 700; color: #F8FAFC;">
                📝 1. Resident Information
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    full_name = st.text_input("Full Legal Name *", placeholder="e.g. Sunita Deshmukh")
    flat_number = st.text_input("Flat / Apartment Number *", placeholder="e.g. D-501 or B-204")
    contact_number = st.text_input("Contact Phone Number (Optional)", placeholder="e.g. +91 98765 43210")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 14px; margin-bottom: 12px;">
            <div style="font-weight: 700; color: #38BDF8; font-size: 0.88rem; margin-bottom: 4px;">🔒 Biometric Privacy & Ethics Confirmation</div>
            <div style="font-size: 0.8rem; color: #94A3B8; line-height: 1.4;">
                In compliance with biometric privacy guidelines, resident photographs and facial embedding vectors are stored locally and encrypted in an isolated SQLite database solely for entrance verification assistance.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    consent_given = st.checkbox("Resident has signed the informed consent declaration for biometric gate access *")

with col_photo:
    st.markdown(
        """
        <div class="security-card">
            <h3 style="margin: 0 0 16px 0; font-size: 1.2rem; font-weight: 700; color: #F8FAFC;">
                📷 2. Biometric Photo Acquisition
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    photo_source = st.radio("Acquisition Source", ["Live Webcam Capture", "Upload Image File"], horizontal=True, label_visibility="collapsed")

    input_img = None
    if photo_source == "Live Webcam Capture":
        cam_photo = st.camera_input("Capture reference portrait")
        if cam_photo:
            input_img = Image.open(cam_photo).convert("RGB")
    else:
        uploaded_file = st.file_uploader("Upload clear frontal image", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            input_img = Image.open(uploaded_file).convert("RGB")

    face_valid = False
    face_encoding = None
    face_crop = None

    if input_img:
        frame_rgb = np.array(input_img)
        faces = detector.detect_faces(frame_rgb)

        st.markdown("##### 🔬 Automated Diagnostic Verification")
        if len(faces) == 0:
            st.error("❌ No face detected. Please ensure subject faces camera directly in good lighting.")
        elif len(faces) > 1:
            st.warning(f"⚠️ {len(faces)} faces detected. Onboarding requires exactly one subject.")
        else:
            quality = detector.assess_face_quality(frame_rgb, faces[0])
            col_q1, col_q2 = st.columns(2)
            with col_q1:
                if quality["is_size_ok"]:
                    st.success("✅ Face Resolution: Pass")
                else:
                    st.error("❌ Resolution: Too small")
            with col_q2:
                if not quality["is_blurred"]:
                    st.success(f"✅ Sharpness: {quality['blur_score']:.1f} (Pass)")
                else:
                    st.error(f"❌ Blurred: {quality['blur_score']:.1f} < 80.0")

            if quality["is_acceptable"]:
                face_crop = quality["face_crop"]
                st.image(face_crop, caption="Normalized Probe Crop (160x160)", width=130)
                try:
                    face_encoding = embedder.generate_embedding(face_crop)
                    face_valid = True
                except Exception as e:
                    st.error(f"Embedding generator error: {e}")

st.markdown("<br>", unsafe_allow_html=True)

# Registration Submit Action
can_submit = bool(full_name and flat_number and consent_given and face_valid and (face_encoding is not None))

col_sub1, col_sub2 = st.columns([3, 1], gap="medium")
with col_sub1:
    if st.button("💾 Enroll & Save Resident Biometric Profile", type="primary", disabled=not can_submit, width="stretch"):
        duplicate = res_mgr.check_duplicate(face_encoding, threshold=0.35)
        if duplicate:
            st.error(
                f"⚠️ Duplicate Face Detected! This biometric profile matches registered resident "
                f"**{duplicate.full_name}** (Flat: **{duplicate.flat_number}**, ID: #{duplicate.resident_id}). "
                f"Registration halted for administrator verification."
            )
        else:
            import io
            img_buf = io.BytesIO()
            input_img.save(img_buf, format="JPEG", quality=92)
            new_id = res_mgr.register_resident(
                full_name=full_name,
                flat_number=flat_number,
                contact_number=contact_number,
                image_bytes=img_buf.getvalue(),
                face_encoding=face_encoding
            )
            st.success(f"🎉 Successfully enrolled resident **{full_name}** (Flat {flat_number}) with Resident ID: **#{new_id}**!")
            st.balloons()

with col_sub2:
    if not can_submit:
        st.caption("Complete all required fields (*), capture a sharp photo, and check consent.")
