import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from database.db import init_db
from modules.resident_manager import ResidentManager
from modules.ui_theme import inject_custom_css, render_sidebar

# Initialize database schema if not present
init_db()

# Page configuration
st.set_page_config(
    page_title="Smart Society Security System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Cyber-Security Theme CSS
inject_custom_css()

# Render Command Sidebar
render_sidebar()

# Hero Header
st.markdown(
    """
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 28px 32px; margin-bottom: 24px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
            <div>
                <span class="badge-pill badge-blue" style="margin-bottom: 8px;">ACCESS CONTROL COMMAND CENTER</span>
                <h1 style="margin: 6px 0 4px 0; font-size: 2.3rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.02em;">
                    Smart Society Security System
                </h1>
                <p style="margin: 0; color: #94A3B8; font-size: 1.05rem;">
                    Local Offline-First AI Facial Recognition, Guard-Assistance & Resident Gate Access Management
                </p>
            </div>
            <div style="text-align: right; background: rgba(15, 23, 42, 0.6); padding: 12px 20px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.06);">
                <div style="font-size: 0.75rem; text-transform: uppercase; color: #64748B; font-weight: 700;">Active Gate Terminal</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #38BDF8;"><span class="status-dot dot-green"></span>Gate Station Alpha</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Navigation Cards Grid
st.markdown("### 🧭 Security Control Hub")

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.markdown(
        """
        <div class="security-card">
            <div style="font-size: 1.8rem; margin-bottom: 8px;">📊</div>
            <h3 style="margin: 0 0 6px 0; font-size: 1.25rem; font-weight: 700; color: #F8FAFC;">Operations Dashboard</h3>
            <p style="color: #94A3B8; font-size: 0.88rem; line-height: 1.5; margin-bottom: 16px;">
                Monitor daily entry volumes, recognition approval rates, gate activity feed, and camera connectivity telemetry.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Operations Dashboard →", key="nav_dash", width="stretch"):
        st.switch_page("pages/1_Dashboard.py")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="security-card">
            <div style="font-size: 1.8rem; margin-bottom: 8px;">📹</div>
            <h3 style="margin: 0 0 6px 0; font-size: 1.25rem; font-weight: 700; color: #F8FAFC;">Live Gate Monitoring</h3>
            <p style="color: #94A3B8; font-size: 0.88rem; line-height: 1.5; margin-bottom: 16px;">
                Real-time webcam video stream with face bounding boxes, 3-tier outcome cards (Green/Yellow/Red), and guard manual overrides.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Launch Live Camera Feed →", key="nav_mon", width="stretch", type="primary"):
        st.switch_page("pages/2_Live_Monitoring.py")

with col2:
    st.markdown(
        """
        <div class="security-card">
            <div style="font-size: 1.8rem; margin-bottom: 8px;">➕</div>
            <h3 style="margin: 0 0 6px 0; font-size: 1.25rem; font-weight: 700; color: #F8FAFC;">Enroll Resident</h3>
            <p style="color: #94A3B8; font-size: 0.88rem; line-height: 1.5; margin-bottom: 16px;">
                Biometric onboarding with webcam capture, automated blur & size checks, consent confirmation, and duplicate detection.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Register New Resident →", key="nav_reg", width="stretch"):
        st.switch_page("pages/3_Register_Resident.py")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="security-card">
            <div style="font-size: 1.8rem; margin-bottom: 8px;">👥</div>
            <h3 style="margin: 0 0 6px 0; font-size: 1.25rem; font-weight: 700; color: #F8FAFC;">Resident Directory</h3>
            <p style="color: #94A3B8; font-size: 0.88rem; line-height: 1.5; margin-bottom: 16px;">
                Search residents by flat number or name, view reference photographs, edit profiles, or toggle active/inactive gate status.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Manage Resident Roster →", key="nav_mgr", width="stretch"):
        st.switch_page("pages/4_Manage_Residents.py")

with col3:
    st.markdown(
        """
        <div class="security-card">
            <div style="font-size: 1.8rem; margin-bottom: 8px;">📜</div>
            <h3 style="margin: 0 0 6px 0; font-size: 1.25rem; font-weight: 700; color: #F8FAFC;">Forensic Audit Logs</h3>
            <p style="color: #94A3B8; font-size: 0.88rem; line-height: 1.5; margin-bottom: 16px;">
                Complete historical record of all gate access attempts, distance scores, reasons, with date filtering and CSV export.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("View Entry History →", key="nav_hist", width="stretch"):
        st.switch_page("pages/5_Entry_History.py")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="security-card">
            <div style="font-size: 1.8rem; margin-bottom: 8px;">📈</div>
            <h3 style="margin: 0 0 6px 0; font-size: 1.25rem; font-weight: 700; color: #F8FAFC;">Benchmark Analytics</h3>
            <p style="color: #94A3B8; font-size: 0.88rem; line-height: 1.5; margin-bottom: 16px;">
                Formal academic evaluation metrics (97.33% Accuracy, 0.00% FAR), confusion matrix heatmap, distance distribution, and reports.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("View Accuracy Benchmark →", key="nav_rep", width="stretch"):
        st.switch_page("pages/6_Analytics.py")
