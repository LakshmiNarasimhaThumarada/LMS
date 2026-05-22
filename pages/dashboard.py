import streamlit as st
import requests
import time
from design_system import *

# Page Config
st.set_page_config(
    page_title="EduMind | Student Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Global CSS
inject_custom_css()

# Dashboard Specific CSS
st.markdown(f"""
<style>
    /* Main Content Background */
    .stApp {{
        background-color: {COLORS['bg_primary']};
    }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: #1f2937 !important;
        border-right: 1px solid #374151 !important;
        min-width: 280px !important;
        max-width: 280px !important;
    }}

    [data-testid="stSidebarContent"] {{
        padding: 24px !important;
        background-color: #1f2937 !important;
    }}

    /* Logo Section */
    .logo-container {{
        margin-bottom: 40px;
    }}
    .logo-text {{
        font-size: 20px;
        font-weight: bold;
        color: {COLORS['text_primary']};
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .logo-tagline {{
        font-size: 14px;
        color: #9ca3af;
        margin-top: 4px;
    }}

    /* Navigation Menu */
    .nav-item {{
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 4px;
        transition: all 0.2s;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 12px;
        color: #f9fafb;
        text-decoration: none;
    }}
    .nav-item:hover {{
        background-color: #2d3748;
    }}
    .nav-item.active {{
        background-color: #374151;
    }}

    /* Logout Button */
    .logout-container {{
        position: absolute;
        bottom: 24px;
        width: calc(100% - 48px);
    }}
    .logout-btn button {{
        width: 100% !important;
        background-color: transparent !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
        padding: 12px !important;
        color: #f9fafb !important;
        transition: all 0.2s !important;
    }}
    .logout-btn button:hover {{
        background-color: #374151 !important;
        border-color: #374151 !important;
    }}

    /* Header Section */
    .welcome-header {{
        font-size: 36px;
        font-weight: bold;
        color: #f9fafb;
        margin-bottom: 16px;
    }}
    .status-text {{
        font-size: 16px;
        color: #9ca3af;
        margin-bottom: 32px;
    }}

    /* Metrics Grid */
    .metrics-row {{
        display: flex;
        gap: 16px;
        margin-bottom: 32px;
        flex-wrap: wrap;
    }}
    .metric-card {{
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 24px;
        flex: 1;
        min-width: 200px;
    }}
    .metric-label {{
        font-size: 12px;
        text-transform: uppercase;
        color: #9ca3af;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .metric-value {{
        font-size: 36px;
        font-weight: bold;
        color: #f9fafb;
    }}

    /* Module Cards */
    .module-grid {{
        display: flex;
        gap: 24px;
        margin-top: 16px;
    }}
    .module-card {{
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 32px;
        flex: 1;
    }}
    .module-header {{
        font-size: 12px;
        color: #3b82f6;
        font-weight: 600;
        margin-bottom: 8px;
        text-transform: uppercase;
    }}
    .module-title {{
        font-size: 24px;
        font-weight: bold;
        color: #f9fafb;
        margin-bottom: 12px;
    }}
    .module-desc {{
        font-size: 14px;
        color: #9ca3af;
        margin-bottom: 24px;
        line-height: 1.5;
    }}

    /* Launch Button Styling (Custom overwrite for Streamlit buttons) */
    div.stButton > button {{
        background: linear-gradient(135deg, {COLORS['accent_blue']} 0%, {COLORS['accent_blue_hover']} 100%) !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
    }}
</style>
""", unsafe_allow_html=True)

# 1. AUTH CHECK
if 'jwt_token' not in st.session_state:
    st.switch_page('pages/login.py')

token = st.session_state.jwt_token
API_BASE = "http://127.0.0.1:6000/api"

# 2. DATA FETCHING
@st.cache_data(ttl=300)
def fetch_dashboard_data(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        # Fetch stats (pdfs, topics, quizzes)
        stats_res = requests.get(f"{API_BASE}/student/stats", headers=headers, timeout=5)
        stats = stats_res.json() if stats_res.status_code == 200 else {}
        
        # Fetch progress (study_hours, streak, avg_score)
        progress_res = requests.get(f"{API_BASE}/student/progress", headers=headers, timeout=5)
        progress = progress_res.json() if progress_res.status_code == 200 else {}
        
        # Combine data
        return {
            "pdfs": stats.get("pdfs", 0),
            "topics": stats.get("topics", 0),
            "quizzes": stats.get("quizzes", 0),
            "study_hours": progress.get("study_hours", 0),
            "streak": progress.get("streak", 0),
            "mastery": progress.get("avg_score", 0)
        }
    except Exception as e:
        st.error(f"Error fetching dashboard data: {e}")
        return {"pdfs": 0, "topics": 0, "quizzes": 0, "study_hours": 0, "streak": 0, "mastery": 0}

@st.cache_data(ttl=3600)
def fetch_user_profile(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.get(f"{API_BASE}/auth/verify", headers=headers, timeout=5)
        if res.status_code == 200:
            return res.json().get('user', {})
        return st.session_state.get('user', {})
    except:
        return st.session_state.get('user', {})

# Load Data
stats = fetch_dashboard_data(token)
user_profile = fetch_user_profile(token)
user_name = user_profile.get('name', 'Student')

# 3. SIDEBAR
with st.sidebar:
    # Logo
    st.markdown("""
        <div class="logo-container">
            <div class="logo-text">🎓 EduMind</div>
            <div class="logo-tagline">Your AI Learning Partner</div>
        </div>
    """, unsafe_allow_html=True)

    # Navigation
    nav_items = [
        ("📊 Dashboard", True),
        ("💬 Chat With AI", False),
        ("📁 My Materials", False),
        ("📝 Generate Quiz", False),
        ("📈 Study Progress", False),
        ("⚙️ Settings", False)
    ]

    for label, active in nav_items:
        active_class = "active" if active else ""
        st.markdown(f'<div class="nav-item {active_class}">{label}</div>', unsafe_allow_html=True)

    # Logout Button at bottom
    st.markdown('<div class="logout-container">', unsafe_allow_html=True)
    if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
        st.session_state.clear()
        st.switch_page('EduMind.py')
    st.markdown('</div>', unsafe_allow_html=True)

# 4. MAIN CONTENT
# Welcome Header
st.markdown(f'<div class="welcome-header">Welcome to EduMind, {user_name}</div>', unsafe_allow_html=True)
st.markdown('<div class="status-text">System ready for deployment. Your academic workspace is synchronized.</div>', unsafe_allow_html=True)

# Performance Metrics Row
cols = st.columns(4)

with cols[0]:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⚡ STUDY VELOCITY</div>
            <div class="metric-value">{stats['study_hours']}h</div>
        </div>
    """, unsafe_allow_html=True)

with cols[1]:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔥 ENGAGEMENT STREAK</div>
            <div class="metric-value">{stats['streak']}</div>
        </div>
    """, unsafe_allow_html=True)

with cols[2]:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🎯 SYSTEM MASTERY</div>
            <div class="metric-value">{stats['mastery']}%</div>
        </div>
    """, unsafe_allow_html=True)

with cols[3]:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🧠 NEURAL SYNC</div>
            <div class="metric-value" style="color: #10b981; font-size: 24px; padding-top: 8px;">Optimal</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Module Cards
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class="module-card">
            <div class="module-header">MODULE 01</div>
            <div class="module-title">AI Knowledge Retrieval</div>
            <div class="module-desc">Access your personalized neural tutor to extract knowledge from your uploaded materials using deep context understanding.</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Launch Module", key="launch_chat"):
        st.switch_page("pages/chat.py")

with col2:
    st.markdown("""
        <div class="module-card">
            <div class="module-header">MODULE 02</div>
            <div class="module-title">Assessment Engine</div>
            <div class="module-desc">Validate your mastery with generated evaluations specifically tailored to your current learning curriculum and progress.</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Launch Module", key="launch_quiz"):
        st.switch_page("pages/quiz.py")

