import streamlit as st
import requests
import time
from design_system import *

# Page Config
st.set_page_config(
    page_title="EduMind | Create Assessment",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Global CSS
inject_custom_css()

# Custom Quiz CSS
st.markdown(f"""
<style>
    /* Configuration Card */
    .config-card {{
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 40px;
        max-width: 800px;
        margin: 0 auto;
    }}

    .config-label {{
        font-size: 16px;
        font-weight: 600;
        color: #f9fafb;
        margin-bottom: 12px;
        display: block;
    }}

    /* Dropdown Overrides */
    div[data-baseweb="select"] {{
        background-color: #111827 !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
    }}
    
    /* Slider Display */
    .difficulty-display {{
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 8px;
    }}
    .diff-easy {{ color: #10b981; }}
    .diff-medium {{ color: #f59e0b; }}
    .diff-hard {{ color: #ef4444; }}

    /* Counter Controls */
    .counter-row {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 24px;
        margin-bottom: 40px;
    }}
    .counter-btn button {{
        width: 44px !important;
        height: 44px !important;
        background-color: #374151 !important;
        border-radius: 8px !important;
        font-size: 20px !important;
        color: #f9fafb !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: none !important;
        box-shadow: none !important;
    }}
    .counter-btn button:hover {{
        background-color: #3b82f6 !important;
        transform: translateY(-2px);
    }}
    .count-display {{
        font-size: 24px;
        font-weight: bold;
        color: #f9fafb;
        width: 60px;
        text-align: center;
    }}

    /* Generate Button */
    .btn-generate button {{
        width: 100% !important;
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        padding: 18px !important;
        border-radius: 12px !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4) !important;
        transition: all 0.3s !important;
        border: none !important;
        color: white !important;
    }}
    .btn-generate button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 28px rgba(59, 130, 246, 0.6) !important;
    }}
</style>
""", unsafe_allow_html=True)

# Auth Check
if 'jwt_token' not in st.session_state:
    st.switch_page('pages/login.py')

API_BASE = "http://localhost:6000/api"
headers = {"Authorization": f"Bearer {st.session_state.jwt_token}"}

# --- Data Fetching ---
def fetch_materials():
    try:
        res = requests.get(f"{API_BASE}/student/pdfs", headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        return []
    except:
        return []

# --- Header ---
st.markdown("""
<div style="margin-bottom: 40px; text-align: center;">
    <div style="font-size: 32px; font-weight: bold; color: #f9fafb; margin-bottom: 8px;">Create Assessment</div>
    <div style="font-size: 16px; color: #9ca3af;">Generate a customized assessment based on your study materials.</div>
</div>
""", unsafe_allow_html=True)

# Initialize Session States for Counter
if 'q_count' not in st.session_state:
    st.session_state.q_count = 5

# --- CONFIGURATION CARD ---
st.markdown('<div class="config-card">', unsafe_allow_html=True)

# 1. SELECT MATERIAL
st.markdown('<label class="config-label">Select Study Material</label>', unsafe_allow_html=True)
materials = fetch_materials()
options = {m['filename']: m['id'] for m in materials}
selected_filename = st.selectbox("Choose a PDF...", options.keys(), label_visibility="collapsed", index=None)

st.markdown('<br>', unsafe_allow_html=True)

# 2. DIFFICULTY SLIDER
st.markdown('<label class="config-label">Assessment Difficulty</label>', unsafe_allow_html=True)
diff_map = {0: "Easy", 1: "Medium", 2: "Hard"}
diff_val = st.select_slider("diff_slider", options=[0, 1, 2], value=1, label_visibility="collapsed")

diff_label = diff_map[diff_val]
diff_class = f"diff-{diff_label.lower()}"
st.markdown(f'<div class="difficulty-display {diff_class}">{diff_label}</div>', unsafe_allow_html=True)

st.markdown('<br>', unsafe_allow_html=True)

# 3. QUESTION COUNT
st.markdown('<label class="config-label" style="text-align: center;">Question Count</label>', unsafe_allow_html=True)

col_minus, col_val, col_plus = st.columns([1, 1, 1])

with col_minus:
    st.markdown('<div class="counter-btn" style="display: flex; justify-content: flex-end;">', unsafe_allow_html=True)
    if st.button("-", key="minus_btn"):
        if st.session_state.q_count > 1:
            st.session_state.q_count -= 1
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_val:
    st.markdown(f'<div class="count-display" style="margin: 0 auto; padding-top: 10px;">{st.session_state.q_count}</div>', unsafe_allow_html=True)

with col_plus:
    st.markdown('<div class="counter-btn">', unsafe_allow_html=True)
    if st.button("+", key="plus_btn"):
        if st.session_state.q_count < 20:
            st.session_state.q_count += 1
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<br>', unsafe_allow_html=True)

# 4. GENERATE BUTTON
st.markdown('<div class="btn-generate">', unsafe_allow_html=True)
if st.button("Initialize Assessment", key="gen_btn"):
    if not selected_filename:
        st.error("Please select a study material first.")
    else:
        with st.spinner("Generating Questions..."):
            try:
                payload = {
                    "pdf_id": options[selected_filename],
                    "difficulty": diff_label.lower(),
                    "num_questions": st.session_state.q_count
                }
                res = requests.post(f"{API_BASE}/quiz/generate", json=payload, headers=headers, timeout=60)
                
                if res.status_code == 201:
                    data = res.json()
                    st.success("Assessment generated successfully!")
                    time.sleep(1)
                    # For demo purposes, we'll store the quiz in session state
                    st.session_state.active_quiz = data
                    # Redirect to a hypothetical quiz take page
                    # st.switch_page("pages/quiz_take.py")
                else:
                    st.error(f"Generation failed: {res.json().get('message', 'Unknown error')}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
