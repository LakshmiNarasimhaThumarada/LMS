import streamlit as st
import requests
import time
import pandas as pd
import plotly.graph_objects as go
from design_system import *

# Page Config
st.set_page_config(
    page_title="EduMind | Admin Panel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Global CSS
inject_custom_css()

# Custom Admin CSS
st.markdown(f"""
<style>
    /* Admin Header */
    .admin-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 40px;
    }}
    .admin-badge {{
        background-color: #ef4444;
        color: white;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        letter-spacing: 0.5px;
    }}

    /* Metrics */
    .admin-metric-card {{
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 24px;
        height: 100%;
    }}
    .a-metric-label {{
        font-size: 12px;
        color: #9ca3af;
        text-transform: uppercase;
        margin-bottom: 8px;
    }}
    .a-metric-value {{
        font-size: 32px;
        font-weight: bold;
        color: #f9fafb;
    }}
    .a-metric-trend {{
        font-size: 14px;
        margin-top: 4px;
    }}

    /* User Management Table */
    .user-row {{
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 8px;
        transition: background-color 0.2s;
    }}
    .user-row:hover {{
        background-color: #374151;
    }}
    
    /* Role Badges */
    .badge-student {{ background-color: #3b82f6; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
    .badge-admin {{ background-color: #ef4444; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }}

    /* Activity Log */
    .activity-row {{
        font-size: 14px;
        padding: 10px 0;
        border-bottom: 1px solid #374151;
        display: flex;
        justify-content: space-between;
    }}
    .activity-user {{ font-weight: 600; color: #3b82f6; }}
    .activity-time {{ color: #6b7280; font-size: 12px; }}

    /* Utils */
    .stat-card {{ background-color: #111827; border: 1px solid #374151; border-radius: 8px; padding: 20px; }}
</style>
""", unsafe_allow_html=True)

# Access Control
user = st.session_state.get('user', {})
if user.get('role') != 'admin':
    st.error("⛔ Access Denied: Admin privileges required")
    time.sleep(2)
    st.switch_page('pages/dashboard.py')
    st.stop()

API_BASE = f"{EXPRESS_URL}/api"
headers = {"Authorization": f"Bearer {st.session_state.jwt_token}"}

# --- Data Fetching ---
def fetch_admin_stats():
    try:
        res = requests.get(f"{API_BASE}/admin/stats", headers=headers, timeout=10)
        return res.json() if res.status_code == 200 else {}
    except: return {}

def fetch_students():
    try:
        res = requests.get(f"{API_BASE}/admin/students", headers=headers, timeout=10)
        return res.json() if res.status_code == 200 else []
    except: return []

def fetch_activity():
    try:
        res = requests.get(f"{API_BASE}/admin/activity", headers=headers, timeout=10)
        return res.json() if res.status_code == 200 else []
    except: return []

# --- Header ---
st.markdown("""
<div class="admin-header">
    <div>
        <div style="font-size: 32px; font-weight: bold; color: #f9fafb;">Admin Dashboard</div>
        <div style="font-size: 16px; color: #9ca3af;">System Administration & User Management</div>
    </div>
    <div class="admin-badge">🔴 ADMIN ACCESS</div>
</div>
""", unsafe_allow_html=True)

# --- TOP METRICS ---
stats = fetch_admin_stats()
col1, col2, col3, col4 = st.columns(4)

metrics = [
    ("Total Students", stats.get('total_students', 0), "👥", "+12 this week", "#10b981"),
    ("Total PDFs", stats.get('total_pdfs', 0), "📚", "Materials", "#9ca3af"),
    ("Total Quizzes", stats.get('total_quizzes', 0), "📝", "Assessments", "#9ca3af"),
    ("System Health", "Operational", "🟢", "All systems normal", "#10b981")
]

for i, (label, val, icon, trend, t_color) in enumerate(metrics):
    with [col1, col2, col3, col4][i]:
        st.markdown(f"""
            <div class="admin-metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div class="a-metric-label">{label}</div>
                    <div style="font-size: 20px;">{icon}</div>
                </div>
                <div class="a-metric-value">{val}</div>
                <div class="a-metric-trend" style="color: {t_color};">{trend}</div>
            </div>
        """, unsafe_allow_html=True)

# --- USER MANAGEMENT ---
st.markdown('<div style="font-size: 24px; font-weight: bold; color: #f9fafb; margin: 40px 0 20px 0;">User Management</div>', unsafe_allow_html=True)

search = st.text_input("Search students...", placeholder="🔍 Search by name or email...", label_visibility="collapsed")
students = fetch_students()

if search:
    students = [s for s in students if search.lower() in s['name'].lower() or search.lower() in s['email'].lower()]

if not students:
    st.info("No matching students found.")
else:
    # Table Header
    cols = st.columns([3, 1.5, 1.5, 1, 1, 2])
    cols[0].markdown('<div class="a-metric-label">User</div>', unsafe_allow_html=True)
    cols[1].markdown('<div class="a-metric-label">Join Date</div>', unsafe_allow_html=True)
    cols[2].markdown('<div class="a-metric-label">Role</div>', unsafe_allow_html=True)
    cols[3].markdown('<div class="a-metric-label">Quizzes</div>', unsafe_allow_html=True)
    cols[4].markdown('<div class="a-metric-label">Avg Score</div>', unsafe_allow_html=True)
    cols[5].markdown('<div class="a-metric-label">Actions</div>', unsafe_allow_html=True)

    for s in students:
        with st.container():
            c = st.columns([3, 1.5, 1.5, 1, 1, 2])
            
            # User Info
            c[0].markdown(f"""
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: #374151; display: flex; align-items: center; justify-content: center; font-size: 12px;">{s['name'][:1]}</div>
                    <div>
                        <div style="font-weight: 600; font-size: 14px;">{s['name']}</div>
                        <div style="color: #6b7280; font-size: 12px;">{s['email']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            c[1].markdown(f'<div style="font-size: 14px; padding-top: 8px;">{s["join_date"]}</div>', unsafe_allow_html=True)
            c[2].markdown('<div style="padding-top: 6px;"><span class="badge-student">Student</span></div>', unsafe_allow_html=True)
            c[3].markdown(f'<div style="font-size: 14px; padding-top: 8px;">{s["quiz_count"]}</div>', unsafe_allow_html=True)
            c[4].markdown(f'<div style="font-size: 14px; padding-top: 8px;">{s["avg_score"]}%</div>', unsafe_allow_html=True)
            
            # Actions
            with c[5]:
                btn_cols = st.columns([1, 1])
                if btn_cols[0].button("Details", key=f"det_{s['id']}"):
                    st.session_state.selected_student = s['id']
                if btn_cols[1].button("🗑️", key=f"del_{s['id']}"):
                    try:
                        res = requests.delete(f"{API_BASE}/admin/student/{s['id']}", headers=headers)
                        if res.status_code == 200:
                            st.toast("User deleted")
                            st.rerun()
                    except: pass
            
            st.markdown('<hr style="margin: 8px 0; border: 0; border-top: 1px solid #374151;">', unsafe_allow_html=True)

# --- STUDENT DETAILS MODAL (Conditional) ---
if 'selected_student' in st.session_state:
    sid = st.session_state.selected_student
    try:
        res = requests.get(f"{API_BASE}/admin/student/{sid}", headers=headers)
        if res.status_code == 200:
            sd = res.json()
            with st.expander(f"📌 Details for {sd['user']['name']}", expanded=True):
                col_i, col_p = st.columns([1, 2])
                with col_i:
                    st.markdown(f"**Email:** {sd['user']['email']}")
                    st.markdown("**Weak Topics:**")
                    for t in sd['weak_topics']:
                        st.markdown(f"- ⚠️ {t}")
                    if st.button("Close Modal"):
                        del st.session_state.selected_student
                        st.rerun()
                with col_p:
                    if sd['quizzes']:
                        df_q = pd.DataFrame(sd['quizzes'])
                        fig = go.Figure(go.Scatter(x=df_q['date'], y=df_q['score'], mode='lines+markers', line=dict(color='#3b82f6')))
                        fig.update_layout(title="Performance History", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#f9fafb'), height=250)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No quiz data available for this student.")
    except: st.error("Failed to load details.")

# --- CHARTS & LOGS ---
col_ch, col_alg = st.columns([2, 1])

with col_ch:
    st.markdown('<div style="font-size: 20px; font-weight: bold; color: #f9fafb; margin: 30px 0 20px 0;">System Performance</div>', unsafe_allow_html=True)
    # Mocking signup data for chart
    signup_data = {"dates": pd.date_range(start="2026-03-01", periods=10), "signups": [2, 5, 3, 8, 4, 10, 6, 9, 7, 12]}
    fig_s = go.Figure(go.Bar(x=signup_data['dates'], y=signup_data['signups'], marker_color='#3b82f6'))
    fig_s.update_layout(title="New Signups (Last 10 Days)", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#f9fafb'), height=300)
    st.plotly_chart(fig_s, use_container_width=True)

with col_alg:
    st.markdown('<div style="font-size: 20px; font-weight: bold; color: #f9fafb; margin: 30px 0 20px 0;">Recent Activity</div>', unsafe_allow_html=True)
    logs = fetch_activity()
    if not logs:
        st.markdown('<div style="color: #6b7280; font-size: 14px;">Refreshing logs...</div>', unsafe_allow_html=True)
    else:
        for l in logs:
            st.markdown(f"""
                <div class="activity-row">
                    <div>
                        <span class="activity-user">{l['user']}</span>
                        <span style="color: #9ca3af;"> {l['action']}</span>
                    </div>
                    <div class="activity-time">{l['timestamp']}</div>
                </div>
            """, unsafe_allow_html=True)

# --- ADMIN CONTROLS ---
st.markdown('<div style="font-size: 24px; font-weight: bold; color: #f9fafb; margin: 40px 0 20px 0;">System Settings</div>', unsafe_allow_html=True)
st.markdown('<div class="stat-card">', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    st.toggle("Enable New User Signups", value=True)
with c2:
    st.toggle("Maintenance Mode", value=False)
with c3:
    if st.button("Generate System Backup", use_container_width=True):
        st.toast("Backup started...")

st.markdown('<br>', unsafe_allow_html=True)
if st.button("Export All System Data (CSV)", use_container_width=True):
    st.toast("Preparing export...")
st.markdown('</div>', unsafe_allow_html=True)
