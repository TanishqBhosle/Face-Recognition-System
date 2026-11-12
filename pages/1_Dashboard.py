import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime

from modules.resident_manager import ResidentManager
from modules.entry_logger import EntryLogger
from modules.ui_theme import inject_custom_css, render_sidebar

st.set_page_config(page_title="Dashboard | Smart Society Security", page_icon="📊", layout="wide")

inject_custom_css()
render_sidebar()

# Page Title & Subtitle Header
st.markdown(
    """
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
        <div>
            <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; color: #F8FAFC;">📊 Security Operations Dashboard</h1>
            <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.95rem;">Real-time access metrics, recognition volume, and gate activity telemetry.</p>
        </div>
        <div style="text-align: right;">
            <span class="badge-pill badge-green"><span class="status-dot dot-green"></span>GATE STATION ALPHA: ACTIVE</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

res_mgr = ResidentManager()
logger = EntryLogger()

# Fetch metrics
active_residents = res_mgr.get_all_active_residents()
total_residents = len(active_residents)
today_summary = logger.get_today_summary()
recent_logs = logger.get_recent_logs(limit=10)

# 5 Sleek Glassmorphic Metric Cards
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-title">Active Residents</div>
            <div class="metric-number">{total_residents}</div>
            <div class="metric-sub">👥 Enrolled & verified</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-title">Today's Probes</div>
            <div class="metric-number">{today_summary['TOTAL']}</div>
            <div class="metric-sub">⚡ Completed gate checks</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-box green">
            <div class="metric-title">Admitted (Green)</div>
            <div class="metric-number" style="color: #34D399;">{today_summary['ENTRY_ALLOWED']}</div>
            <div class="metric-sub">✅ Confident matches</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-box red">
            <div class="metric-title">Denied (Red)</div>
            <div class="metric-number" style="color: #F87171;">{today_summary['ENTRY_REJECTED']}</div>
            <div class="metric-sub">🛑 Unregistered / Strangers</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col5:
    st.markdown(
        f"""
        <div class="metric-box yellow">
            <div class="metric-title">Review (Yellow)</div>
            <div class="metric-number" style="color: #FBBF24;">{today_summary['VERIFICATION_REQUIRED']}</div>
            <div class="metric-sub">⚠️ Manual guard checks</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# Mid Section: Camera Node Health & Access Distribution Chart
col_cam, col_chart = st.columns([1, 2], gap="large")

with col_cam:
    st.markdown(
        """
        <div class="security-card" style="height: 100%;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px;">
                <h4 style="margin:0; font-size: 1.1rem; color: #F8FAFC;">📹 Live Camera Node</h4>
                <span class="badge-pill badge-green">FEED READY</span>
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 14px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 16px;">
                <div style="display:flex; justify-content:space-between; margin-bottom: 8px; font-size: 0.85rem;">
                    <span style="color: #94A3B8;">Webcam Device</span>
                    <span style="color: #F8FAFC; font-weight:600;">Index 0 (Built-in)</span>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom: 8px; font-size: 0.85rem;">
                    <span style="color: #94A3B8;">Inference Pipeline</span>
                    <span style="color: #38BDF8; font-weight:600;">Facenet512 (Cosine)</span>
                </div>
                <div style="display:flex; justify-content:space-between; font-size: 0.85rem;">
                    <span style="color: #94A3B8;">Quality Guard</span>
                    <span style="color: #34D399; font-weight:600;">Laplacian &ge; 80.0</span>
                </div>
            </div>
            <p style="font-size: 0.82rem; color: #64748B; line-height: 1.4; margin-bottom: 16px;">
                The monitoring station executes local face detection and threshold comparisons in real time.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("🚀 Switch to Live Monitoring Feed", width="stretch", type="primary"):
        st.switch_page("pages/2_Live_Monitoring.py")

with col_chart:
    st.markdown(
        """
        <div class="security-card">
            <h4 style="margin: 0 0 12px 0; font-size: 1.1rem; color: #F8FAFC;">📈 Today's Decision Breakdown</h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    dist_data = {
        "Outcome": ["Admitted (Green)", "Denied (Red)", "Manual Review (Yellow)"],
        "Probes": [
            max(1, today_summary["ENTRY_ALLOWED"]),
            today_summary["ENTRY_REJECTED"],
            today_summary["VERIFICATION_REQUIRED"]
        ],
        "Color": ["#10B981", "#EF4444", "#F59E0B"]
    }
    df_dist = pd.DataFrame(dist_data)
    fig = px.pie(
        df_dist,
        values="Probes",
        names="Outcome",
        color="Outcome",
        color_discrete_map={
            "Admitted (Green)": "#10B981",
            "Denied (Red)": "#EF4444",
            "Manual Review (Yellow)": "#F59E0B"
        },
        hole=0.55
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94A3B8", family="Plus Jakarta Sans"),
        margin=dict(t=10, b=10, l=10, r=10),
        height=240,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, width="stretch")

st.markdown("<br>", unsafe_allow_html=True)

# Bottom Section: Recent Gate Activity Timeline
st.markdown("### 🕒 Recent Gate Activity Stream")

if recent_logs:
    display_rows = []
    for log in recent_logs:
        status_badge = {
            "ENTRY_ALLOWED": "🟢 ALLOWED",
            "ENTRY_REJECTED": "🔴 REJECTED",
            "VERIFICATION_REQUIRED": "🟡 VERIFY"
        }.get(log["decision"], log["decision"])

        resident_str = f"{log['full_name']} ({log['flat_number']})" if log["full_name"] else "Unknown Individual"
        display_rows.append({
            "Event ID": f"#{log['log_id']}",
            "Timestamp": log["timestamp"],
            "Subject Identity": resident_str,
            "Gate Decision": status_badge,
            "Cosine Metric": f"{log['match_distance']:.3f}",
            "System Audit Reason": log["reason"]
        })
    df_recent = pd.DataFrame(display_rows)
    st.dataframe(df_recent, width="stretch", hide_index=True)
else:
    st.info("No gate events recorded yet today.")
