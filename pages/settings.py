import streamlit as st
import requests
import time
from design_system import *

# Page Config
st.set_page_config(
    page_title="EduMind | Settings",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Global CSS
inject_custom_css()

# Custom Settings CSS
st.markdown(f"""
<style>
    /* Settings Grid Layout */
    .settings-container {{
        display: flex;
        gap: 24px;
        margin-top: 24px;
    }}
    
    /* Settings Menu (Sidebar) */
    .settings-menu {{
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 16px;
        height: fit-content;
    }}
    .menu-item {{
        padding: 14px 20px;
        border-radius: 8px;
        color: #9ca3af;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 4px;
        text-decoration: none;
        border-left: 3px solid transparent;
    }}
    .menu-item:hover {{
        background-color: #2d3748;
        color: #f9fafb;
    }}
    .menu-item.active {{
        background-color: #374151;
        color: #f9fafb;
        border-left: 3px solid #3b82f6;
    }}

    /* Content Area */
    .content-section {{
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 32px;
        margin-bottom: 24px;
    }}
    .section-title {{
        font-size: 20px;
        font-weight: bold;
        color: #f9fafb;
        margin-bottom: 24px;
    }}

    /* Form Elements */
    .field-label {{
        font-size: 14px;
        color: #9ca3af;
        margin-bottom: 8px;
        display: block;
    }}
    
    /* Avatar */
    .avatar-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 32px;
    }}
    .avatar-circle {{
        width: 80px;
        height: 80px;
        background-color: #374151;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        color: #3b82f6;
        border: 2px solid #3b82f6;
        margin-bottom: 12px;
    }}

    /* Toggle Row */
    .toggle-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #374151;
    }}
    .toggle-label {{
        color: #f9fafb;
        font-size: 16px;
    }}

    /* Support Cards */
    .support-card {{
        background-color: #111827;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.2s;
        cursor: pointer;
    }}
    .support-card:hover {{
        border-color: #3b82f6;
        background-color: #1a1f2e;
    }}

    /* Buttons */
    .btn-save button {{
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4) !important;
    }}
    .btn-delete button {{
        background-color: rgba(239, 68, 68, 0.1) !important;
        color: #ef4444 !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
    }}
</style>
""", unsafe_allow_html=True)

# Auth Check
if 'jwt_token' not in st.session_state:
    st.switch_page('pages/login.py')

# Initialize Session State for Active Tab
if 'settings_tab' not in st.session_state:
    st.session_state.settings_tab = "👤 Profile"

# API Logic
def save_settings(data, endpoint="/api/user/profile"):
    # In real app: requests.put(f"http://localhost:6000{endpoint}", json=data, headers=headers)
    st.toast("Settings saved successfully!", icon="✅")

# --- HEADER ---
st.markdown("""
<div style="margin-bottom: 32px;">
    <div style="font-size: 32px; font-weight: bold; color: #f9fafb; margin-bottom: 8px;">Settings</div>
    <div style="font-size: 16px; color: #9ca3af;">Manage your account and preferences</div>
</div>
""", unsafe_allow_html=True)

# --- LAYOUT: TWO COLUMNS ---
col_menu, col_content = st.columns([1, 2.5])

# LEFT: SETTINGS MENU
with col_menu:
    st.markdown('<div class="settings-menu">', unsafe_allow_html=True)
    menu_items = [
        "👤 Profile", "🔔 Notifications", "🎨 Appearance", 
        "🔒 Privacy & Security", "💳 Subscription", "❓ Help & Support"
    ]
    
    for item in menu_items:
        active_class = "active" if st.session_state.settings_tab == item else ""
        # We'll use buttons styled as menu items for interactivity
        if st.button(item, key=f"menu_{item}", use_container_width=True, 
                     type="secondary"):
            st.session_state.settings_tab = item
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# RIGHT: CONTENT AREA
with col_content:
    st.markdown(f'<div class="section-title">{st.session_state.settings_tab}</div>', unsafe_allow_html=True)
    
    # 1. PROFILE TAB
    if st.session_state.settings_tab == "👤 Profile":
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title" style="font-size: 18px;">Account Information</div>', unsafe_allow_html=True)
        
        # Avatar
        st.markdown("""
            <div class="avatar-container">
                <div class="avatar-circle">JD</div>
            </div>
        """, unsafe_allow_html=True)
        st.file_uploader("Upload Photo", type=["jpg", "png"], label_visibility="collapsed")
        
        # Fields
        user = st.session_state.get('user', {"name": "John Doe", "email": "john@example.com"})
        
        st.markdown('<span class="field-label">Full Name</span>', unsafe_allow_html=True)
        new_name = st.text_input("name_input", value=user['name'], label_visibility="collapsed")
        
        st.markdown('<br><span class="field-label">Email Address</span>', unsafe_allow_html=True)
        new_email = st.text_input("email_input", value=user['email'], label_visibility="collapsed")
        
        st.markdown('<br>', unsafe_allow_html=True)
        if st.button("Change Password"):
            st.info("Password reset link sent to your email.")
            
        st.markdown('<div style="text-align: right; margin-top: 32px;">', unsafe_allow_html=True)
        st.markdown('<div class="btn-save">', unsafe_allow_html=True)
        if st.button("Save Changes", key="save_profile"):
            save_settings({"name": new_name, "email": new_email})
        st.markdown('</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. NOTIFICATIONS TAB
    elif st.session_state.settings_tab == "🔔 Notifications":
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        
        toggles = [
            ("Email notifications", True),
            ("Quiz reminders", True),
            ("Study streak alerts", False),
            ("New feature announcements", True)
        ]
        
        for label, default in toggles:
            c1, c2 = st.columns([4, 1])
            with c1: st.markdown(f'<div style="padding-top: 5px;">{label}</div>', unsafe_allow_html=True)
            with c2: st.toggle(label, value=default, key=f"tog_{label}", label_visibility="collapsed")
            st.markdown('<hr style="margin: 8px 0; border-top: 1px solid #374151;">', unsafe_allow_html=True)
            
        st.markdown('<div style="text-align: right; margin-top: 32px;">', unsafe_allow_html=True)
        st.markdown('<div class="btn-save">', unsafe_allow_html=True)
        if st.button("Save Preferences"):
            save_settings({}, "/api/user/settings")
        st.markdown('</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. APPEARANCE TAB
    elif st.session_state.settings_tab == "🎨 Appearance":
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        
        st.markdown('<span class="field-label">Theme</span>', unsafe_allow_html=True)
        st.radio("theme_select", ["Dark Mode (Recommended)", "Light Mode", "System Default"], 
                 label_visibility="collapsed")
        
        st.markdown('<br><span class="field-label">Font Size</span>', unsafe_allow_html=True)
        st.select_slider("font_slider", options=["Small", "Medium", "Large"], value="Medium", 
                         label_visibility="collapsed")
        
        st.markdown('<div style="text-align: right; margin-top: 32px;">', unsafe_allow_html=True)
        st.markdown('<div class="btn-save">', unsafe_allow_html=True)
        if st.button("Apply Appearance"):
            st.toast("Appearance updated!", icon="🎨")
        st.markdown('</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 4. PRIVACY & SECURITY TAB
    elif st.session_state.settings_tab == "🔒 Privacy & Security":
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title" style="font-size: 16px;">Two-Factor Authentication</div>', unsafe_allow_html=True)
        st.toggle("Enable 2FA", value=False)
        
        st.markdown('<br><div class="section-title" style="font-size: 16px;">Data Portability</div>', unsafe_allow_html=True)
        st.button("Request Data Export")
        
        st.markdown('<br><div class="section-title" style="font-size: 16px; color: #ef4444;">Danger Zone</div>', unsafe_allow_html=True)
        st.markdown('<div class="btn-delete">', unsafe_allow_html=True)
        if st.button("Delete Account", use_container_width=True):
            st.error("Account deletion is a permanent action.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 6. HELP & SUPPORT
    elif st.session_state.settings_tab == "❓ Help & Support":
        supports = [
            ("📚 Documentation", "Access detailed guides and tutorials."),
            ("💬 Contact Support", "Email us at support@edumind.ai"),
            ("🐛 Report a Bug", "Help us improve the neural network.")
        ]
        
        for title, desc in supports:
            st.markdown(f"""
                <div class="support-card">
                    <div style="font-weight: bold; color: #f9fafb; margin-bottom: 4px;">{title}</div>
                    <div style="font-size: 14px; color: #9ca3af;">{desc}</div>
                </div>
            """, unsafe_allow_html=True)
    
    else:
        st.info("This section is under active synchronization.")
