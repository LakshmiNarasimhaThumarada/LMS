import streamlit as st
import requests
import re
import time
from design_system import *

# Page Config
st.set_page_config(
    page_title="EduMind - Sign Up",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Global Design System Injection
inject_custom_css()

# Custom CSS for Login/Signup centered layout
st.markdown(f"""
<style>
    /* Center the login card */
    .stApp {{
        background: radial-gradient(circle at top right, #1a2332, #0f1419);
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    
    .login-card {{
        background: {COLORS['bg_secondary']};
        border: 1px solid {COLORS['border_default']};
        border-radius: {RADIUS['xl']};
        padding: {SPACING['12']};
        width: 100%;
        max-width: 500px;
        box-shadow: {SHADOWS['xl']};
        margin: auto;
    }}
    
    .auth-header {{
        text-align: center;
        margin-bottom: {SPACING['8']};
    }}
    
    .auth-title {{
        font-size: {TYPOGRAPHY['3xl']};
        font-weight: {FONT_WEIGHTS['bold']};
        color: {COLORS['text_primary']};
        margin-bottom: {SPACING['2']};
    }}
    
    .auth-subtitle {{
        font-size: {TYPOGRAPHY['base']};
        color: {COLORS['text_tertiary']};
    }}
    
    /* Field Labels */
    .field-label {{
        display: block;
        margin-bottom: {SPACING['2']};
        font-weight: {FONT_WEIGHTS['medium']};
        color: {COLORS['text_secondary']};
        font-size: {TYPOGRAPHY['sm']};
    }}
    
    /* Styled Input Wrapper */
    .stTextInput > div > div > input {{
        background: #111827 !important;
        border: 1px solid #374151 !important;
        border-radius: {RADIUS['lg']} !important;
        padding: 14px 16px !important;
        color: white !important;
        transition: all 0.2s ease !important;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: {COLORS['accent_blue']} !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }}
    
    /* Error Text */
    .error-text {{
        color: {COLORS['accent_error']};
        font-size: 14px;
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    
    /* Primary Button */
    div[data-testid="stButton"] button[key="signup_submit"] {{
        width: 100% !important;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        padding: 16px !important;
        border: none !important;
        border-radius: {RADIUS['lg']} !important;
        font-weight: {FONT_WEIGHTS['semibold']} !important;
        font-size: 18px !important;
        margin-top: {SPACING['8']} !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
        transition: all 0.3s ease !important;
    }}
    
    div[data-testid="stButton"] button[key="signup_submit"]:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.4) !important;
    }}

    /* Password Strength Indicator */
    .strength-bar-container {{
        height: 4px;
        background: #374151;
        border-radius: 2px;
        margin-top: 8px;
        overflow: hidden;
    }}
    
    .strength-bar {{
        height: 100%;
        transition: width 0.3s ease, background 0.3s ease;
    }}
    
    .strength-text {{
        font-size: 12px;
        margin-top: 4px;
        font-weight: {FONT_WEIGHTS['medium']};
    }}

    .footer-links {{
        text-align: center;
        margin-top: {SPACING['8']};
        font-size: {TYPOGRAPHY['sm']};
        color: {COLORS['text_tertiary']};
    }}

    /* Hide Streamlit elements */
    [data-testid="stHeader"], [data-testid="stFooter"] {{
        visibility: hidden;
    }}
</style>
""", unsafe_allow_html=True)

def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def check_password_strength(password):
    if not password:
        return 0, "None", "#374151"
    
    strength = 0
    if len(password) >= 8: strength += 1
    if any(c.isupper() for c in password) and any(c.islower() for c in password): strength += 1
    if any(c.isdigit() for c in password) or any(not c.isalnum() for c in password): strength += 1
    
    if strength <= 1:
        return 33, "Weak", "#ef4444"
    elif strength == 2:
        return 66, "Medium", "#f59e0b"
    else:
        return 100, "Strong", "#10b981"

# Signup Logic
def signup_user(name, email, password):
    API_URL = f"{EXPRESS_URL}/api/auth/signup"
    try:
        response = requests.post(API_URL, json={
            "name": name,
            "email": email,
            "password": password
        }, timeout=60)
        if response.status_code in [200, 201]:
            return response.json(), None
        else:
            error_data = response.json()
            return None, error_data.get("message", "Registration failed")
    except Exception as e:
        return None, f"Connection failed: {str(e)}"

# Session State
if 'signup_error' not in st.session_state:
    st.session_state.signup_error = None
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False

# Layout
with st.container():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    # Header
    st.markdown(f'''
        <div class="auth-header">
            <div class="auth-title">Create Your Account</div>
            <div class="auth-subtitle">Start your learning journey with EduMind</div>
        </div>
    ''', unsafe_allow_html=True)

    # Form
    st.markdown('<label class="field-label">Full Name</label>', unsafe_allow_html=True)
    name = st.text_input("name_input", label_visibility="collapsed", placeholder="John Doe")
    
    st.markdown('<label class="field-label" style="margin-top: 24px;">Email Address</label>', unsafe_allow_html=True)
    email = st.text_input("email_input", label_visibility="collapsed", placeholder="you@example.com")
    
    st.markdown('<label class="field-label" style="margin-top: 24px;">Password</label>', unsafe_allow_html=True)
    password = st.text_input("password_input", label_visibility="collapsed", type="password", placeholder="••••••••")
    
    # Strength Indicator
    strength_val, strength_label, strength_color = check_password_strength(password)
    st.markdown(f'''
        <div class="strength-bar-container">
            <div class="strength-bar" style="width: {strength_val}%; background: {strength_color};"></div>
        </div>
        <div class="strength-text" style="color: {strength_color};">{strength_label}</div>
    ''', unsafe_allow_html=True)
    
    st.markdown('<label class="field-label" style="margin-top: 24px;">Confirm Password</label>', unsafe_allow_html=True)
    confirm_password = st.text_input("confirm_input", label_visibility="collapsed", type="password", placeholder="••••••••")

    # Error Display
    if st.session_state.signup_error:
        st.markdown(f'<p class="error-text">⚠️ {st.session_state.signup_error}</p>', unsafe_allow_html=True)

    # Submit Button
    btn_text = "Creating Account..." if st.session_state.is_loading else "Create Account"
    if st.button(btn_text, key="signup_submit", disabled=st.session_state.is_loading):
        if not name or len(name) < 2:
            st.session_state.signup_error = "Name must be at least 2 characters"
        elif not email or not validate_email(email):
            st.session_state.signup_error = "Please enter a valid email address"
        elif not password or len(password) < 8:
            st.session_state.signup_error = "Password must be at least 8 characters"
        elif password != confirm_password:
            st.session_state.signup_error = "Passwords do not match"
        else:
            st.session_state.is_loading = True
            st.rerun()

    # Processing
    if st.session_state.is_loading:
        data, error = signup_user(name, email, password)
        st.session_state.is_loading = False
        if data:
            st.session_state['jwt_token'] = data.get('token')
            st.session_state['user'] = data.get('user')
            st.success("Account created successfully! Entering workspace...")
            time.sleep(1)
            st.rerun()
        else:
            st.session_state.signup_error = error
            st.rerun()

    # Footer
    st.markdown('<div class="footer-links">Already have an account?</div>', unsafe_allow_html=True)
    if st.button("Log In", key="goto_login"):
        st.switch_page("pages/login.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Additional CSS to style the footer button as a link
st.markdown(f"""
<style>
    /* Footer Button as Link */
    div[data-testid="stButton"] button[key="goto_login"] {{
        background: transparent !important;
        border: none !important;
        color: {COLORS['accent_blue']} !important;
        padding: 0 !important;
        font-size: {TYPOGRAPHY['sm']} !important;
        font-weight: {FONT_WEIGHTS['semibold']} !important;
        box-shadow: none !important;
        margin: -10px auto 0 auto !important;
        display: block !important;
        width: auto !important;
    }}
    div[data-testid="stButton"] button[key="goto_login"]:hover {{
        text-decoration: underline !important;
        transform: none !important;
        background: transparent !important;
    }}
</style>
""", unsafe_allow_html=True)
