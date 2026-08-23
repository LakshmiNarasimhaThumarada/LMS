import streamlit as st
import os

# API Endpoint Configurations (load dynamically from env or fallback to local)
EXPRESS_URL = os.getenv("EXPRESS_URL", "http://127.0.0.1:6000").rstrip("/")
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000").rstrip("/")

# ==========================================
# DESIGN TOKENS
# ==========================================

# Color Palette
COLORS = {
    # Backgrounds
    'bg_primary': '#0f1419',      # Main app background
    'bg_secondary': '#1f2937',    # Cards, panels, sidebar
    'bg_tertiary': '#111827',     # Input fields, hover states
    'bg_overlay': 'rgba(0,0,0,0.6)',  # Modal overlays
    
    # Borders
    'border_default': '#374151',  # Default borders
    'border_focus': '#3b82f6',    # Focused elements
    'border_subtle': '#1f2937',   # Very subtle dividers
    
    # Text
    'text_primary': '#f9fafb',    # Main headings, body text
    'text_secondary': '#9ca3af',  # Labels, descriptions
    'text_tertiary': '#6b7280',   # Disabled, placeholder text
    'text_inverse': '#111827',    # Text on light backgrounds
    
    # Accents
    'accent_blue': '#3b82f6',     # Primary CTA buttons
    'accent_blue_hover': '#2563eb',
    'accent_blue_light': 'rgba(59, 130, 246, 0.1)',
    'accent_success': '#10b981',  # Success messages
    'accent_warning': '#f59e0b',  # Warnings
    'accent_error': '#ef4444',    # Errors, validation
    'accent_purple': '#8b5cf6',   # Secondary actions
}

# Typography Scale (8px base)
TYPOGRAPHY = {
    'xs': '12px',     # Tiny labels, timestamps
    'sm': '14px',     # Small body text
    'base': '16px',   # Default body text
    'lg': '18px',     # Emphasized text
    'xl': '20px',     # Section subtitles
    '2xl': '24px',    # Page titles
    '3xl': '30px',    # Dashboard metrics
    '4xl': '36px',    # Large metrics
    '5xl': '48px',    # Hero text
    '6xl': '56px',    # Landing page hero
}

# Font Weights
FONT_WEIGHTS = {
    'normal': 400,
    'medium': 500,
    'semibold': 600,
    'bold': 700,
}

# Spacing Scale (8px base system)
SPACING = {
    '1': '8px',
    '2': '16px',
    '3': '24px',
    '4': '32px',
    '5': '40px',
    '6': '48px',
    '8': '64px',
    '10': '80px',
    '12': '96px',
}

# Border Radius
RADIUS = {
    'sm': '6px',
    'md': '8px',
    'lg': '12px',
    'xl': '16px',
    'full': '9999px',
}

# Shadows
SHADOWS = {
    'sm': '0 1px 2px rgba(0,0,0,0.05)',
    'md': '0 4px 6px rgba(0,0,0,0.1)',
    'lg': '0 10px 15px rgba(0,0,0,0.1)',
    'xl': '0 20px 25px rgba(0,0,0,0.1)',
    'glow_blue': '0 4px 20px rgba(59, 130, 246, 0.4)',
}

# Transitions
TRANSITIONS = {
    'fast': '150ms ease-in-out',
    'normal': '200ms ease-in-out',
    'slow': '300ms ease-in-out',
}

# ==========================================
# REUSABLE COMPONENTS
# ==========================================

def inject_custom_css():
    """Inject global CSS for entire app - call this at the start of every page"""
    st.markdown(f"""
    <style>
    /* Reset and Base Styles */
    .stApp {{
        background-color: {COLORS['bg_primary']};
        color: {COLORS['text_primary']};
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}
    
    /* Hide Streamlit Branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: {COLORS['bg_secondary']} !important;
        border-right: 1px solid {COLORS['border_default']} !important;
    }}
    
    /* Clean Sidebar Nav Links */
    [data-testid="stSidebarNavLink"] {{
        border-radius: {RADIUS['md']} !important;
        margin: 4px 12px !important;
        padding: 8px 12px !important;
        font-weight: {FONT_WEIGHTS['medium']} !important;
        transition: all {TRANSITIONS['fast']} !important;
    }}
    
    [data-testid="stSidebarNavLink"]:hover {{
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: {COLORS['text_primary']} !important;
    }}
    
    [data-testid="stSidebarNavLink"][aria-current="page"] {{
        background: linear-gradient(135deg, {COLORS['accent_blue']} 0%, {COLORS['accent_blue_hover']} 100%) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }}
    
    /* Sidebar Button overrides (e.g. Logout button) */
    [data-testid="stSidebar"] button {{
        background: transparent !important;
        border: 1px solid {COLORS['accent_error']} !important;
        color: {COLORS['accent_error']} !important;
        font-weight: {FONT_WEIGHTS['semibold']} !important;
        border-radius: {RADIUS['md']} !important;
        transition: all {TRANSITIONS['fast']} !important;
        box-shadow: none !important;
        width: 100% !important;
    }}
    
    [data-testid="stSidebar"] button:hover {{
        background: {COLORS['accent_error']} !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3) !important;
    }}
    
    /* Input Fields */
    .stTextInput input, .stTextArea textarea {{
        background-color: {COLORS['bg_tertiary']} !important;
        border: 1px solid {COLORS['border_default']} !important;
        color: {COLORS['text_primary']} !important;
        border-radius: {RADIUS['md']} !important;
        padding: 12px 16px !important;
        font-size: {TYPOGRAPHY['base']} !important;
    }}
    
    .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: {COLORS['border_focus']} !important;
        box-shadow: 0 0 0 3px {COLORS['accent_blue_light']} !important;
    }}
    
    /* Buttons */
    .stButton button {{
        background: linear-gradient(135deg, {COLORS['accent_blue']} 0%, {COLORS['accent_blue_hover']} 100%);
        color: white;
        border: none;
        border-radius: {RADIUS['lg']};
        padding: 14px 32px;
        font-weight: {FONT_WEIGHTS['semibold']};
        font-size: {TYPOGRAPHY['base']};
        transition: all {TRANSITIONS['normal']};
        box-shadow: {SHADOWS['glow_blue']};
    }}
    
    .stButton button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 28px rgba(59, 130, 246, 0.6);
    }}
    
    /* Cards */
    .card {{
        background-color: {COLORS['bg_secondary']};
        border: 1px solid {COLORS['border_default']};
        border-radius: {RADIUS['lg']};
        padding: {SPACING['3']};
        margin-bottom: {SPACING['2']};
    }}
    
    /* Success/Error Messages */
    .stSuccess, .stError, .stWarning {{
        border-radius: {RADIUS['md']};
        padding: {SPACING['2']};
    }}
    </style>
    """, unsafe_allow_html=True)

def create_card(content, padding=SPACING['3']):
    """Create a styled card container"""
    return f"""
    <div style="
        background-color: {COLORS['bg_secondary']};
        border: 1px solid {COLORS['border_default']};
        border-radius: {RADIUS['lg']};
        padding: {padding};
        margin-bottom: {SPACING['2']};
    ">
        {content}
    </div>
    """

def create_metric_card(label, value, subtitle='', icon='📊'):
    """Create a metric display card"""
    return f"""
    <div style="
        background-color: {COLORS['bg_secondary']};
        border: 1px solid {COLORS['border_default']};
        border-radius: {RADIUS['lg']};
        padding: {SPACING['3']};
        text-align: center;
    ">
        <div style="font-size: {TYPOGRAPHY['3xl']}; margin-bottom: {SPACING['1']};">{icon}</div>
        <div style="
            font-size: {TYPOGRAPHY['xs']};
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: {COLORS['text_secondary']};
            margin-bottom: {SPACING['1']};
        ">{label}</div>
        <div style="
            font-size: {TYPOGRAPHY['4xl']};
            font-weight: {FONT_WEIGHTS['bold']};
            color: {COLORS['text_primary']};
            margin-bottom: 4px;
        ">{value}</div>
        {f"<div style='font-size: {TYPOGRAPHY['sm']}; color: {COLORS['text_tertiary']};'>{subtitle}</div>" if subtitle else ''}
    </div>
    """

def create_button(text, variant='primary', fullwidth=False):
    """Create a styled button"""
    styles = {
        'primary': f'background: linear-gradient(135deg, {COLORS["accent_blue"]} 0%, {COLORS["accent_blue_hover"]} 100%); color: white;',
        'secondary': f'background: transparent; border: 2px solid {COLORS["border_default"]}; color: {COLORS["text_secondary"]};',
        'success': f'background: {COLORS["accent_success"]}; color: white;',
        'danger': f'background: {COLORS["accent_error"]}; color: white;'
    }
    
    width = 'width: 100%;' if fullwidth else ''
    
    return f"""
    <button style="
        {styles.get(variant, styles['primary'])}
        border: none;
        border-radius: {RADIUS['lg']};
        padding: 14px 32px;
        font-weight: {FONT_WEIGHTS['semibold']};
        font-size: {TYPOGRAPHY['base']};
        cursor: pointer;
        transition: all {TRANSITIONS['normal']};
        box-shadow: {SHADOWS['glow_blue']};
        {width}
    " onmouseover="this.style.transform='translateY(-2px)'" 
       onmouseout="this.style.transform='translateY(0)'">
        {text}
    </button>
    """

def render_top_navbar():
    """Render custom horizontal top navigation bar across all pages"""
    if 'user' not in st.session_state:
        return
        
    import inspect
    import os
    
    # Detect active page from call stack
    active_page = ""
    for frame_info in inspect.stack():
        filename = frame_info.filename
        if "pages" in filename:
            active_page = os.path.basename(filename)
            break

    # JS Trigger to expand/collapse sidebar automatically based on page
    is_active_chat_str = "true" if active_page == "chat.py" else "false"
    
    js_code = """
    <script>
    const parentDoc = window.parent.document;
    const collapseBtn = parentDoc.querySelector('button[data-testid="stSidebarCollapseButton"]');
    const expandBtn = parentDoc.querySelector('button[data-testid="stCollapsedSidebarCollapsed"]') || 
                      parentDoc.querySelector('[data-testid="collapsedSidebarCollapsed"]') ||
                      parentDoc.querySelector('.collapsed-sidebar-collapsed') ||
                      parentDoc.querySelector('button[class*="collapsedSidebarCollapsed"]') ||
                      parentDoc.querySelector('button[aria-label="Expand sidebar"]');
    
    const isActiveChat = IS_ACTIVE_CHAT;
    
    if (isActiveChat) {
        // Expand sidebar if on chat page
        if (expandBtn) {
            expandBtn.click();
        }
    } else {
        // Collapse sidebar on all other pages for full display width
        if (collapseBtn) {
            collapseBtn.click();
        }
    }
    </script>
    """.replace("IS_ACTIVE_CHAT", is_active_chat_str)
    
    import streamlit.components.v1 as components
    components.html(js_code, height=0, width=0)

    # CSS to style navbar block and align buttons
    st.markdown("""
    <style>
    /* Align all columns inside the top navbar horizontally and center them vertically */
    div[data-testid="stBlock"] > div[data-testid="stHorizontalBlock"]:first-of-type {
        align-items: center !important;
        background-color: #1f2937 !important;
        border: 1px solid #374151 !important;
        border-radius: 12px !important;
        padding: 8px 16px !important;
        margin-bottom: 24px !important;
    }
    
    /* Remove vertical spacing offset for navbar buttons */
    div[data-testid="stBlock"] > div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    div[data-testid="stBlock"] > div[data-testid="stHorizontalBlock"]:first-of-type button {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Use 8 columns: Brand + 6 page links + Logout
    cols = st.columns([1.6, 1.2, 1.2, 1.2, 1.2, 1.2, 1.1, 1.1])
    
    with cols[0]:
        st.markdown("<div style='font-size: 20px; font-weight: bold; color: #f9fafb;'>🎓 EduMind</div>", unsafe_allow_html=True)
        
    pages_config = [
        ("🏠 Dashboard", "pages/dashboard.py", "dashboard.py"),
        ("💬 Chat", "pages/chat.py", "chat.py"),
        ("📂 Materials", "pages/upload.py", "upload.py"),
        ("🎯 Quiz", "pages/quiz.py", "quiz.py"),
        ("📊 Progress", "pages/progress.py", "progress.py"),
        ("⚙️ Settings", "pages/settings.py", "settings.py"),
    ]
    
    for idx, (label, path, filename) in enumerate(pages_config, start=1):
        with cols[idx]:
            is_active = (filename == active_page)
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{filename}", use_container_width=True, type=btn_type):
                st.switch_page(path)
                
    with cols[7]:
        if st.button("🚪 Logout", key="nav_logout", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.switch_page("pages/landing.py")

