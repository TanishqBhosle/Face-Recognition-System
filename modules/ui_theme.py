import streamlit as st

def inject_custom_css():
    """
    Injects enterprise-grade, dark glassmorphism cyber-security styling across Streamlit pages.
    Features modern typography, glowing status indicators, sleek cards, and animated badges.
    """
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

            /* Global Font and Background */
            html, body, [class*="css"] {
                font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            }
            
            /* Main Content Container Styling */
            .main .block-container {
                padding-top: 1.8rem;
                padding-bottom: 2.5rem;
                max-width: 1380px;
            }

            /* Custom Cyber-Security Glassmorphism Cards */
            .security-card {
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 14px;
                padding: 20px;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
                margin-bottom: 16px;
                transition: transform 0.2s ease, border-color 0.2s ease;
            }
            .security-card:hover {
                border-color: rgba(59, 130, 246, 0.4);
                transform: translateY(-2px);
            }

            /* Metric Display Card */
            .metric-box {
                background: linear-gradient(145deg, #1E293B 0%, #0F172A 100%);
                border: 1px solid rgba(255, 255, 255, 0.07);
                border-radius: 12px;
                padding: 16px 20px;
                position: relative;
                overflow: hidden;
            }
            .metric-box::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, #3B82F6, #60A5FA);
            }
            .metric-box.green::before { background: linear-gradient(90deg, #10B981, #34D399); }
            .metric-box.red::before { background: linear-gradient(90deg, #EF4444, #F87171); }
            .metric-box.yellow::before { background: linear-gradient(90deg, #F59E0B, #FBBF24); }

            .metric-title {
                font-size: 0.8rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: #94A3B8;
                margin-bottom: 6px;
            }
            .metric-number {
                font-size: 2.2rem;
                font-weight: 800;
                color: #F8FAFC;
                line-height: 1;
                font-feature-settings: "tnum";
            }
            .metric-sub {
                font-size: 0.78rem;
                color: #64748B;
                margin-top: 6px;
                font-weight: 500;
            }

            /* Live Pulsing Dot Indicator */
            .status-dot {
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 8px;
                vertical-align: middle;
            }
            .dot-green {
                background-color: #10B981;
                box-shadow: 0 0 10px #10B981, 0 0 20px rgba(16, 185, 129, 0.5);
                animation: pulse-green 2s infinite;
            }
            .dot-amber {
                background-color: #F59E0B;
                box-shadow: 0 0 10px #F59E0B;
                animation: pulse-amber 2s infinite;
            }
            .dot-red {
                background-color: #EF4444;
                box-shadow: 0 0 10px #EF4444;
            }

            @keyframes pulse-green {
                0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
                70% { transform: scale(1.05); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
                100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
            }

            /* Recognition HUD Decision Cards */
            .hud-decision-allowed {
                background: linear-gradient(135deg, rgba(6, 78, 59, 0.9) 0%, rgba(6, 95, 70, 0.95) 100%);
                border: 2px solid #10B981;
                border-radius: 16px;
                padding: 24px;
                text-align: center;
                box-shadow: 0 12px 30px rgba(16, 185, 129, 0.25);
            }
            .hud-decision-verify {
                background: linear-gradient(135deg, rgba(120, 53, 15, 0.9) 0%, rgba(146, 64, 14, 0.95) 100%);
                border: 2px solid #F59E0B;
                border-radius: 16px;
                padding: 24px;
                text-align: center;
                box-shadow: 0 12px 30px rgba(245, 158, 11, 0.25);
            }
            .hud-decision-reject {
                background: linear-gradient(135deg, rgba(127, 29, 29, 0.9) 0%, rgba(153, 27, 27, 0.95) 100%);
                border: 2px solid #EF4444;
                border-radius: 16px;
                padding: 24px;
                text-align: center;
                box-shadow: 0 12px 30px rgba(239, 68, 68, 0.25);
            }

            /* Subject ID Badge Card */
            .subject-badge {
                background: rgba(30, 41, 59, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 16px;
                display: flex;
                gap: 16px;
                align-items: center;
            }
            .subject-avatar {
                width: 90px;
                height: 90px;
                border-radius: 10px;
                object-fit: cover;
                border: 2px solid rgba(255, 255, 255, 0.2);
            }

            /* Custom Pill Tags */
            .badge-pill {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 700;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            }
            .badge-green { background-color: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid #10B981; }
            .badge-amber { background-color: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid #F59E0B; }
            .badge-red { background-color: rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid #EF4444; }
            .badge-blue { background-color: rgba(59, 130, 246, 0.15); color: #60A5FA; border: 1px solid #3B82F6; }

            /* Modern Table Styling */
            .stDataFrame, div[data-testid="stTable"] {
                border-radius: 12px;
                overflow: hidden;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }

            /* Custom Scrollbars */
            ::-webkit-scrollbar {
                width: 7px;
                height: 7px;
            }
            ::-webkit-scrollbar-track {
                background: #0F172A;
            }
            ::-webkit-scrollbar-thumb {
                background: #334155;
                border-radius: 4px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: #475569;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_sidebar():
    """Renders the high-end security command station sidebar."""
    from modules.resident_manager import ResidentManager
    res_mgr = ResidentManager()
    active_count = len(res_mgr.get_all_active_residents())

    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 10px 0;">
                <div style="display:flex; align-items:center; gap: 10px;">
                    <div style="font-size: 1.8rem;">🏢</div>
                    <div>
                        <div style="font-size: 1.1rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.02em;">AURA GUARD</div>
                        <div style="font-size: 0.72rem; color: #38BDF8; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;">Smart Society Security</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.divider()

        st.markdown(
            f"""
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 12px 14px; margin-bottom: 16px;">
                <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; font-weight: 700; margin-bottom: 8px;">Station Telemetry</div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 0.85rem; color: #E2E8F0;"><span class="status-dot dot-green"></span>Webcam Node</span>
                    <span class="badge-pill badge-green" style="padding: 2px 8px; font-size: 0.68rem;">ONLINE</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 0.85rem; color: #E2E8F0;"><span class="status-dot dot-green"></span>SQLite Engine</span>
                    <span class="badge-pill badge-green" style="padding: 2px 8px; font-size: 0.68rem;">READY</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.85rem; color: #E2E8F0;">Active Roster</span>
                    <span class="badge-pill badge-blue" style="padding: 2px 8px; font-size: 0.68rem;">{active_count} Enrolled</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### 🛡️ Operator Auth")
        if st.session_state.get("admin_logged_in", False):
            st.markdown(
                f"""
                <div style="padding: 8px 12px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; margin-bottom: 10px;">
                    <span style="font-size: 0.85rem; color: #34D399;">🔑 Authenticated as <b>{st.session_state.get('admin_username', 'Admin')}</b></span>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("Sign Out", width="stretch", key="sb_logout_btn"):
                st.session_state.admin_logged_in = False
                st.session_state.admin_username = ""
                st.rerun()
        else:
            st.markdown(
                """
                <div style="padding: 8px 12px; background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 8px; margin-bottom: 10px;">
                    <span style="font-size: 0.8rem; color: #93C5FD;">Guard Duty Mode (Restricted)</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            with st.expander("Admin Login"):
                u = st.text_input("User", key="sb_user")
                p = st.text_input("Pass", type="password", key="sb_pass")
                if st.button("Authenticate", width="stretch", key="sb_login_btn"):
                    if u == "admin" and p == "admin123":
                        st.session_state.admin_logged_in = True
                        st.session_state.admin_username = "admin"
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")

        st.divider()
        st.markdown(
            """
            <div style="font-size: 0.72rem; color: #64748B; text-align: center;">
                Smart Society Security v1.0<br>
                Edge AI • Offline Biometric Guard
            </div>
            """,
            unsafe_allow_html=True
        )

