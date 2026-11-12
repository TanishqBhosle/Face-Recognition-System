import sys
from pathlib import Path
from datetime import datetime, timedelta
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import pandas as pd
from modules.entry_logger import EntryLogger
from modules.ui_theme import inject_custom_css, render_sidebar

st.set_page_config(page_title="Entry History | Smart Society Security", page_icon="📜", layout="wide")

inject_custom_css()
render_sidebar()

# Page Header
st.markdown(
    """
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
        <div>
            <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; color: #F8FAFC;">📜 Forensic Entry History & Audit Trail</h1>
            <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.95rem;">Cryptographically timestamped gate access records with distance metrics and forensic reasons.</p>
        </div>
        <div style="text-align: right;">
            <span class="badge-pill badge-green">AUDIT LOGGING: ACTIVE</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

logger = EntryLogger()

# Filter Controls Card
st.markdown(
    """
    <div class="security-card" style="padding: 16px 20px; margin-bottom: 20px;">
        <div style="font-weight: 700; color: #38BDF8; font-size: 0.88rem; margin-bottom: 12px;">🔍 Forensic Search & Filter Toolbar</div>
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns([1, 1, 2], gap="medium")
with col1:
    date_range = st.date_input(
        "Audit Date Window",
        value=(datetime.now().date() - timedelta(days=14), datetime.now().date())
    )
with col2:
    decision_choice = st.selectbox(
        "Access Decision Status",
        ["ALL", "ENTRY_ALLOWED", "ENTRY_REJECTED", "VERIFICATION_REQUIRED"]
    )
with col3:
    query = st.text_input("Full-Text Search", placeholder="Filter by resident name, flat number, or diagnostic reason...")

start_d = str(date_range[0]) if isinstance(date_range, (tuple, list)) and len(date_range) > 0 else None
end_d = str(date_range[1]) if isinstance(date_range, (tuple, list)) and len(date_range) > 1 else start_d

# Query records
logs = logger.search_logs(
    start_date=start_d,
    end_date=end_d,
    decision_filter=decision_choice,
    query=query,
    limit=500
)

# Statistics bar
col_s1, col_s2 = st.columns([3, 1])
with col_s1:
    st.markdown(f"**Found `{len(logs)}` forensic log records matching current filter criteria.**")
with col_s2:
    if logs:
        df_export = pd.DataFrame(logs)
        csv_bytes = df_export.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Audit Trail (CSV)",
            data=csv_bytes,
            file_name=f"society_gate_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            type="primary",
            width="stretch"
        )

# Display Table
if logs:
    display_data = []
    for log in logs:
        badge = {
            "ENTRY_ALLOWED": "🟢 ALLOWED",
            "ENTRY_REJECTED": "🔴 REJECTED",
            "VERIFICATION_REQUIRED": "🟡 VERIFY"
        }.get(log["decision"], log["decision"])

        identity = f"{log['full_name']} ({log['flat_number']})" if log["full_name"] else "Unknown Subject"
        display_data.append({
            "Log ID": f"#{log['log_id']}",
            "Timestamp": log["timestamp"],
            "Identified Subject": identity,
            "Gate Decision": badge,
            "Cosine Metric": f"{log['match_distance']:.3f}",
            "Forensic Note": log["reason"]
        })

    df = pd.DataFrame(display_data)
    st.dataframe(df, width="stretch", hide_index=True)
else:
    st.info("No gate access records found for the selected filter range.")
