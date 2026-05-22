import streamlit as st
import time
from design_system import *

def inject_error_css():
    st.markdown("""
    <style>
        /* Center Layout */
        .error-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 80vh;
            text-align: center;
            padding: 48px;
            animation: fadeIn 0.5s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Error Card */
        .error-card {
            background-color: #1f2937;
            border: 1px solid #374151;
            border-radius: 16px;
            padding: 60px;
            max-width: 600px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        /* Icon Animation */
        .error-icon {
            font-size: 80px;
            margin-bottom: 24px;
            animation: bounce 2s infinite ease-in-out;
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-15px); }
        }

        /* Error Code & Text */
        .error-code {
            font-size: 84px;
            font-weight: 800;
            letter-spacing: -4px;
            line-height: 1;
            margin-bottom: 16px;
        }
        .error-title {
            font-size: 32px;
            font-weight: 700;
            color: #f9fafb;
            margin-bottom: 16px;
        }
        .error-msg {
            font-size: 18px;
            color: #9ca3af;
            line-height: 1.6;
            margin-bottom: 40px;
            max-width: 450px;
        }

        /* Action Buttons */
        .error-actions {
            display: flex;
            gap: 16px;
            justify-content: center;
            width: 100%;
        }
        
        /* Custom Button Overrides */
        .btn-primary-error button {
            background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            color: white !important;
            border-radius: 10px !important;
            border: none !important;
        }
        .btn-secondary-error button {
            background: transparent !important;
            border: 1px solid #374151 !important;
            color: #f9fafb !important;
            padding: 12px 24px !important;
            border-radius: 10px !important;
        }
    </style>
    """, unsafe_allow_html=True)

def show_error(error_type='404', custom_message=None):
    # Ensure design system is injected
    inject_custom_css()
    inject_error_css()
    
    # State mapping
    errors = {
        '404': {
            'icon': '🔍',
            'code': '404',
            'title': 'Page Not Found',
            'msg': "The page you're looking for doesn't exist or has been moved.",
            'color': '#3b82f6',
            'primary': 'Go to Dashboard',
            'secondary': 'Contact Support'
        },
        '500': {
            'icon': '⚠️',
            'code': '500',
            'title': 'Server Error',
            'msg': "Something went wrong on our end. We're working on fixing it.",
            'color': '#ef4444',
            'primary': 'Try Again',
            'secondary': 'Report Issue'
        },
        'expired': {
            'icon': '⏰',
            'code': '!',
            'title': 'Session Expired',
            'msg': "Your current session has timed out. Please log in again to continue.",
            'color': '#f59e0b',
            'primary': 'Log In',
            'secondary': None
        },
        'maintenance': {
            'icon': '🔧',
            'code': '...',
            'title': 'Under Maintenance',
            'msg': "EduMind is undergoing a scheduled upgrade. We'll be back online shortly.",
            'color': '#3b82f6',
            'primary': 'Check Status',
            'secondary': 'Documentation'
        },
        'network': {
            'icon': '📡',
            'code': 'OFFLINE',
            'title': 'Connection Lost',
            'msg': "Please check your internet connection and try reloading the page.",
            'color': '#ef4444',
            'primary': 'Retry',
            'secondary': None
        }
    }

    err = errors.get(str(error_type), errors['404'])
    msg = custom_message if custom_message else err['msg']

    # Render Template
    st.markdown(f"""
    <div class="error-wrapper">
        <div class="error-card">
            <div class="error-icon">{err['icon']}</div>
            <div class="error-code" style="color: {err['color']};">{err['code']}</div>
            <div class="error-title">{err['title']}</div>
            <div class="error-msg">{msg}</div>
            <div id="error-btn-anchor"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Render Buttons using st.columns within the container logic
    # (Since we can't easily nest st.button inside raw markdown without placeholders)
    # Using a 2nd container for layout control
    with st.container():
        # Adjust layout for buttons
        b_col1, b_col2 = st.columns([1, 1])
        
        # Primary Button Action
        with b_col1:
            st.markdown('<div class="btn-primary-error">', unsafe_allow_html=True)
            if st.button(err['primary'], key="err_primary"):
                if error_type == '404' or error_type == '500':
                    st.switch_page('pages/dashboard.py')
                elif error_type == 'expired':
                    st.switch_page('pages/login.py')
                elif error_type == 'network':
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Secondary Button Action
        if err['secondary']:
            with b_col2:
                st.markdown('<div class="btn-secondary-error">', unsafe_allow_html=True)
                if st.button(err['secondary'], key="err_secondary"):
                    st.toast("Redirecting to support center...")
                st.markdown('</div>', unsafe_allow_html=True)

# Main entry for stand-alone use
if __name__ == '__main__':
    st.set_page_config(page_title="EduMind | Error", page_icon="🚫", layout="centered")
    # Determine type from query params or default
    query_params = st.query_params
    e_type = query_params.get("type", "404")
    show_error(e_type)
