import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import pandas as pd
from PIL import Image
import numpy as np

from modules.resident_manager import ResidentManager
from modules.face_detector import FaceDetector
from modules.face_recognition import EmbeddingModel
from modules.ui_theme import inject_custom_css, render_sidebar

st.set_page_config(page_title="Manage Residents | Smart Society Security", page_icon="👥", layout="wide")

inject_custom_css()
render_sidebar()

# Page Header
st.markdown(
    """
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
        <div>
            <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; color: #F8FAFC;">👥 Resident Directory & Management</h1>
            <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.95rem;">Search, inspect photographs, update profiles, or toggle gate access authorization.</p>
        </div>
        <div style="text-align: right;">
            <span class="badge-pill badge-blue">ADMIN ACCESS CONSOLE</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

res_mgr = ResidentManager()
detector = FaceDetector()
embedder = EmbeddingModel.get_instance()

# Filter Toolbar
col_search, col_filter = st.columns([3, 1], gap="medium")
with col_search:
    search_query = st.text_input("🔍 Search Residents (Name or Flat)", placeholder="e.g. Sharma or A-101")
with col_filter:
    status_filter = st.selectbox("Status Filter", ["ALL", "ACTIVE", "INACTIVE"])

all_residents = res_mgr.get_all_residents()

filtered = []
for r in all_residents:
    if status_filter != "ALL" and r["status"] != status_filter:
        continue
    if search_query:
        q = search_query.lower()
        if q not in r["full_name"].lower() and q not in r["flat_number"].lower():
            continue
    filtered.append(r)

st.caption(f"Showing **{len(filtered)}** of **{len(all_residents)}** registered society residents.")

# View Tabs: Table View vs. Visual Cards Grid
tab_grid, tab_cards, tab_edit = st.tabs(["📋 Tabular Directory", "🪪 Visual Cards Roster", "⚙️ Profile & Biometric Editor"])

with tab_grid:
    if filtered:
        df = pd.DataFrame([
            {
                "Resident ID": f"#{r['resident_id']}",
                "Full Name": r["full_name"],
                "Flat Number": r["flat_number"],
                "Contact Number": r["contact_number"] or "-",
                "Access Status": "🟢 ACTIVE" if r["status"] == "ACTIVE" else "🔴 INACTIVE",
                "Enrollment Date": r["created_at"][:10]
            }
            for r in filtered
        ])
        st.dataframe(df, width="stretch", hide_index=True)
    else:
        st.info("No residents match your search criteria.")

with tab_cards:
    if filtered:
        # Display in a 3-column responsive card grid
        cols = st.columns(3)
        for idx, r in enumerate(filtered):
            with cols[idx % 3]:
                photo_path = Path(r["image_path"])
                status_class = "badge-green" if r["status"] == "ACTIVE" else "badge-red"
                st.markdown(
                    f"""
                    <div class="security-card" style="padding: 16px; margin-bottom: 16px;">
                        <div style="display: flex; gap: 12px; align-items: center;">
                            <img src="{str(photo_path) if photo_path.exists() else 'https://via.placeholder.com/60'}" 
                                 style="width: 60px; height: 60px; border-radius: 8px; object-fit: cover; border: 1px solid rgba(255,255,255,0.2);" />
                            <div style="flex: 1; overflow: hidden;">
                                <div style="font-weight: 700; color: #F8FAFC; font-size: 1.0rem; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">
                                    {r['full_name']}
                                </div>
                                <div style="margin-top: 4px; display: flex; gap: 6px;">
                                    <span class="badge-pill badge-blue" style="padding: 1px 6px; font-size: 0.68rem;">{r['flat_number']}</span>
                                    <span class="badge-pill {status_class}" style="padding: 1px 6px; font-size: 0.68rem;">{r['status']}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("No residents match your filter.")

with tab_edit:
    st.markdown("#### Manage Profile Details & Biometric Image")
    resident_options = {f"#{r['resident_id']} - {r['full_name']} ({r['flat_number']})": r["resident_id"] for r in all_residents}
    if resident_options:
        selected_label = st.selectbox("Select resident profile to inspect/edit:", list(resident_options.keys()))
        selected_id = resident_options[selected_label]
        selected_res = res_mgr.get_resident_by_id(selected_id)

        if selected_res:
            col_v, col_e = st.columns([1, 2], gap="large")
            with col_v:
                st.markdown("##### Reference Biometric Portrait")
                img_path = Path(selected_res.image_path)
                if img_path.exists():
                    st.image(str(img_path), width=180, caption=f"ID #{selected_res.resident_id}")
                else:
                    st.info("Photo file not found on disk.")

                st.markdown("<br>", unsafe_allow_html=True)
                new_status = "INACTIVE" if selected_res.status == "ACTIVE" else "ACTIVE"
                btn_label = "🚫 Revoke Gate Access (Set Inactive)" if selected_res.status == "ACTIVE" else "✅ Restore Gate Access (Set Active)"
                btn_type = "secondary" if selected_res.status == "ACTIVE" else "primary"
                if st.button(btn_label, width="stretch", type=btn_type):
                    res_mgr.set_status(selected_res.resident_id, new_status)
                    st.success(f"Status changed to {new_status}!")
                    st.rerun()

            with col_e:
                st.markdown("##### Edit Resident Details")
                with st.form(f"edit_form_{selected_res.resident_id}"):
                    edit_name = st.text_input("Full Name", value=selected_res.full_name)
                    edit_flat = st.text_input("Flat Number", value=selected_res.flat_number)
                    edit_contact = st.text_input("Contact Phone", value=selected_res.contact_number or "")
                    
                    if st.form_submit_button("💾 Save Profile Updates", type="primary"):
                        res_mgr.update_resident(selected_res.resident_id, edit_name, edit_flat, edit_contact)
                        st.success("Resident metadata successfully updated!")
                        st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("##### Replace Biometric Photograph")
                new_photo = st.file_uploader(f"Upload fresh portrait for #{selected_res.resident_id}", type=["jpg", "jpeg", "png"], key=f"photo_{selected_res.resident_id}")
                if new_photo and st.button("🔄 Recalculate Embedding & Save Photo"):
                    img = Image.open(new_photo).convert("RGB")
                    frame_rgb = np.array(img)
                    faces = detector.detect_faces(frame_rgb)
                    if len(faces) == 1:
                        quality = detector.assess_face_quality(frame_rgb, faces[0])
                        new_encoding = embedder.generate_embedding(quality["face_crop"])
                        import io
                        buf = io.BytesIO()
                        img.save(buf, format="JPEG", quality=92)
                        res_mgr.update_photo_and_embedding(selected_res.resident_id, buf.getvalue(), new_encoding)
                        st.success("Biometric photograph and embedding updated!")
                        st.rerun()
                    else:
                        st.error(f"Image must contain exactly 1 face (detected {len(faces)}).")
    else:
        st.info("No residents enrolled.")
