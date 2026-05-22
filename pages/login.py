import streamlit as st
import requests
import re
import time
from design_system import *

# Page Config
st.set_page_config(
    page_title="EduMind | Log In",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject Global CSS
inject_custom_css()

# Custom Login Page CSS
st.markdown(f"""
<style>
    /* Center the login card */
    .stApp {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 100vh !important;
        background: {COLORS['bg_primary']} !important;
    }}
    
    .main .block-container {{
        max-width: 500px !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }}

    /* Login Card Container */
    .login-card {{
        background: {COLORS['bg_secondary']};
        border: 1px solid {COLORS['border_default']};
        border-radius: {RADIUS['xl']};
        padding: {SPACING['6']};
        box-shadow: {SHADOWS['xl']};
        width: 100%;
        max-width: 500px;
        margin: auto;
    }}

    /* Global Typography Overrides for Login */
    .login-title {{
        font-size: {TYPOGRAPHY['3xl']};
        font-weight: {FONT_WEIGHTS['bold']};
        color: {COLORS['text_primary']};
        text-align: center;
        margin-bottom: {SPACING['2']};
    }}

    .login-subtitle {{
        font-size: {TYPOGRAPHY['base']};
        color: {COLORS['text_secondary']};
        text-align: center;
        margin-bottom: {SPACING['5']};
    }}

    /* Label Styling */
    .field-label {{
        font-size: {TYPOGRAPHY['sm']};
        font-weight: {FONT_WEIGHTS['medium']};
        color: {COLORS['text_primary']};
        margin-bottom: {SPACING['1']};
        display: block;
    }}

    /* Error Message Styling */
    .error-text {{
        color: {COLORS['accent_error']};
        font-size: {TYPOGRAPHY['sm']};
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 4px;
    }}

    /* Button Styling */
    div[data-testid="stButton"] button {{
        width: 100% !important;
        background: linear-gradient(135deg, {COLORS['accent_blue']}, {COLORS['accent_blue_hover']}) !important;
        color: white !important;
        padding: 16px !important;
        border-radius: {RADIUS['lg']} !important;
        font-size: {TYPOGRAPHY['lg']} !important;
        font-weight: {FONT_WEIGHTS['semibold']} !important;
        box-shadow: {SHADOWS['glow_blue']} !important;
        border: none !important;
        margin-top: {SPACING['4']} !important;
        transition: all {TRANSITIONS['normal']} !important;
    }}

    div[data-testid="stButton"] button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6) !important;
    }}

    div[data-testid="stButton"] button:disabled {{
        opacity: 0.6 !important;
        cursor: not-allowed !important;
        transform: none !important;
    }}

    /* Footer Links */
    .footer-links {{
        text-align: center;
        margin-top: {SPACING['5']};
        font-size: {TYPOGRAPHY['sm']};
        color: {COLORS['text_secondary']};
    }}

    .footer-links a {{
        color: {COLORS['accent_blue']};
        text-decoration: none;
        font-weight: {FONT_WEIGHTS['semibold']};
    }}

    .forgot-link {{
        text-align: center;
        margin-top: {SPACING['2']};
        font-size: {TYPOGRAPHY['sm']};
        color: {COLORS['text_tertiary']};
    }}

    /* Hide Streamlit elements */
    [data-testid="stHeader"], [data-testid="stFooter"] {{
        visibility: hidden;
    }}
    
    /* Responsive Adjustments */
    @media (max-width: 500px) {{
        .login-card {{
            padding: {SPACING['4']};
            border: none;
            box-shadow: none;
            background: transparent;
        }}
    }}
</style>
""", unsafe_allow_html=True)

def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Authentication logic
def login_user(email, password):
    API_URL = "http://127.0.0.1:6000/api/auth/login"
    try:
        response = requests.post(API_URL, json={"email": email, "password": password}, timeout=10)
        if response.status_code == 200:
            return response.json(), None
        else:
            error_data = response.json()
            return None, error_data.get("error", "Invalid credentials")
    except Exception as e:
        return None, "Connection failed. Please ensure the backend is running."

# Login Page UI
with st.container():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    st.markdown('<div class="login-title">Welcome Back</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Log in to your EduMind account</div>', unsafe_allow_html=True)
    
    # Form initialization
    if 'login_error' not in st.session_state:
        st.session_state.login_error = ""

    # Email Field
    st.markdown('<label class="field-label">Email</label>', unsafe_allow_html=True)
    email = st.text_input("email_input", label_visibility="collapsed", placeholder="you@example.com")
    if email and not validate_email(email):
        st.markdown('<p class="error-text">⚠️ Please enter a valid email</p>', unsafe_allow_html=True)

    # Password Field
    st.markdown('<label class="field-label" style="margin-top: 16px;">Password</label>', unsafe_allow_html=True)
    password = st.text_input("password_input", label_visibility="collapsed", type="password", placeholder="••••••••")

    # Error Display
    if st.session_state.login_error:
        st.markdown(f'<p class="error-text" style="color: {COLORS["accent_error"]};">⚠️ {st.session_state.login_error}</p>', unsafe_allow_html=True)

    # Submit Button
    btn_text = "Logging in..." if st.session_state.get('is_loading', False) else "Log In"
    if st.button(btn_text, key="login_btn", disabled=st.session_state.get('is_loading', False)):
        if not email or not validate_email(email):
            st.session_state.login_error = "Please enter a valid email address"
        elif not password:
            st.session_state.login_error = "Password cannot be empty"
        else:
            st.session_state.is_loading = True
            st.rerun()

    # Authentication Processing (after rerun)
    if st.session_state.get('is_loading', False):
        data, error = login_user(email, password)
        st.session_state.is_loading = False
        if data:
            st.session_state['jwt_token'] = data.get('token')
            st.session_state['user'] = data.get('user')
            role = data.get('user', {}).get('role', 'student')
            st.success("Authentication successful! Redirecting...")
            time.sleep(0.8)
            st.rerun() # Use rerun so EduMind.py registers new navigation
        else:
            st.session_state.login_error = error
            st.rerun()

    # Footer
    st.markdown('<div class="footer-links">Don\'t have an account?</div>', unsafe_allow_html=True)
    if st.button("Sign Up", key="goto_signup", help="Create a new account"):
        st.switch_page("pages/signup.py")
        
    st.markdown('<div class="forgot-link">Forgot Password?</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Additional CSS to style the footer button as a link
st.markdown(f"""
<style>
    /* Footer Button as Link */
    div[data-testid="stButton"] button[key="goto_signup"] {{
        background: transparent !important;
        border: none !important;
        color: {COLORS['accent_blue']} !important;
        padding: 0 !important;
        font-size: {TYPOGRAPHY['sm']} !important;
        font-weight: {FONT_WEIGHTS['semibold']} !important;
        box-shadow: none !important;
        margin: -10px auto {SPACING['2']} auto !important;
        display: block !important;
        width: auto !important;
        text-decoration: none !important;
    }}
    div[data-testid="stButton"] button[key="goto_signup"]:hover {{
        text-decoration: underline !important;
        transform: none !important;
        background: transparent !important;
    }}
</style>
""", unsafe_allow_html=True)
