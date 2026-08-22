import streamlit as st
from design_system import *
import design_system

# Initialize sidebar state in session state
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = "expanded"

# MUST be the first streamlit command
st.set_page_config(
    page_title="EduMind - Your Personal AI Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state=st.session_state.sidebar_state
)

# Apply Global Design System
inject_custom_css()


# Navigation Engine
def sidebar_branding():
    st.sidebar.markdown(f"""
    <div style="padding: {SPACING['2']} 0; text-align: center;">
        <span style="font-size: 2.5rem;">🎓</span>
        <h2 style="margin: 0; font-weight: {FONT_WEIGHTS['bold']}; color: {COLORS['text_primary']};">EduMind</h2>
        <p style="color: {COLORS['text_secondary']}; font-size: {TYPOGRAPHY['xs']}; margin-top: 5px;">Your AI Learning Partner</p>
    </div>
    <hr style="margin: 10px 0; border-color: {COLORS['border_default']};">
    """, unsafe_allow_html=True)

# Navigation Engine
if 'user' not in st.session_state:
    # Public Pages
    pages = [
        st.Page("pages/landing.py", title="EduMind", icon="🎓", default=True),
        st.Page("pages/login.py", title="Login", icon="🔐"),
        st.Page("pages/signup.py", title="Sign Up", icon="📝"),
    ]
    pg = st.navigation(pages, position="hidden")
    pg.run()
else:
    user = st.session_state['user']
    role = user.get('role', 'student')

    # Build Navigation
    if role == 'admin':
        pages = [
            st.Page("pages/admin.py", title="Admin Dashboard", icon="🛡️", default=True),
            st.Page("pages/settings.py", title="Settings", icon="⚙️"),
        ]
    else:
        pages = [
            st.Page("pages/dashboard.py", title="Dashboard", icon="🏠", default=True),
            st.Page("pages/chat.py", title="Chat With AI", icon="💬"),
            st.Page("pages/upload.py", title="My Materials", icon="📂"),
            st.Page("pages/quiz.py", title="Generate Quiz", icon="🎯"),
            st.Page("pages/progress.py", title="Study Progress", icon="📊"),
            st.Page("pages/settings.py", title="Settings", icon="⚙️"),
        ]
    
    pg = st.navigation(pages, position="hidden")
    
    # Render custom top navigation bar
    design_system.render_top_navbar()
        
    pg.run()
