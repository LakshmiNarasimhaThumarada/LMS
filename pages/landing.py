import streamlit as st
from design_system import *

# Inject Global CSS
inject_custom_css()

# Custom Landing Page CSS
st.markdown(f"""
<style>
    /* Hero Container */
    .hero-container {{
        background: linear-gradient(180deg, {COLORS['bg_primary']} 0%, #1a2332 100%);
        min-height: 60vh; /* Reduced from 90vh/100vh for natural flow */
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: {SPACING['12']} {SPACING['6']} {SPACING['6']} {SPACING['6']}; /* Increased bottom breathing room */
        position: relative;
        overflow: hidden;
    }}

    /* Floating Background Orbs */
    .orb-1 {{
        position: absolute;
        top: 15%; /* Higher orb */
        left: 10%;
        width: 300px;
        height: 300px;
        background: {COLORS['accent_blue']};
        filter: blur(120px);
        opacity: 0.1;
        border-radius: 50%;
        z-index: 0;
        animation: float 10s ease-in-out infinite alternate;
    }}
    .orb-2 {{
        position: absolute;
        bottom: 15%; /* adjusted position */
        right: 15%;
        width: 400px;
        height: 400px;
        background: {COLORS['accent_purple']};
        filter: blur(150px);
        opacity: 0.08;
        border-radius: 50%;
        z-index: 0;
        animation: float 15s ease-in-out infinite alternate-reverse;
    }}

    @keyframes float {{
        0% {{ transform: translate(0, 0); }}
        100% {{ transform: translate(30px, -20px); }}
    }}

    /* Content Wrapper */
    .hero-content {{
        max-width: 1200px;
        width: 100%;
        z-index: 1;
        opacity: 0;
        animation: fadeIn 0.8s ease-out forwards;
        margin-top: 0; /* Reset margin */
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Typography */
    .eyebrow {{
        font-size: 110px; /* Massive size for brand presence */
        color: {COLORS['text_primary']};
        text-transform: uppercase;
        letter-spacing: 6px; /* Increased letter spacing */
        margin-bottom: {SPACING['1']};
        font-weight: 800; /* Extra bold */
        line-height: 0.9;
    }}

    .headline {{
        font-size: 32px; /* Decreased size */
        font-weight: {FONT_WEIGHTS['semibold']};
        color: {COLORS['accent_blue']}; /* Changed color to blue for secondary emphasis */
        line-height: 1.2;
        letter-spacing: 0px;
        margin-bottom: {SPACING['6']};
        white-space: pre-line;
    }}

    .subheadline {{
        font-size: {TYPOGRAPHY['xl']};
        color: {COLORS['text_secondary']};
        line-height: 1.6;
        max-width: 850px;
        width: 100%;
        margin-left: auto !important;
        margin-right: auto !important;
        margin-bottom: {SPACING['6']}; /* Reduced for better proximity to buttons */
        text-align: center !important;
        display: block;
    }}

    /* Buttons Layout */
    .cta-group {{
        display: flex;
        gap: {SPACING['3']};
        justify-content: center;
        opacity: 0;
        animation: slideUp 0.8s ease-out 0.4s forwards;
    }}

    @keyframes slideUp {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Custom Button Overrides for this page */
    .stButton > button {{
        width: auto !important;
        margin: 0 !important;
    }}

    /* Mobile Responsive */
    @media (max-width: 768px) {{
        .headline {{
            font-size: 42px;
            letter-spacing: -1px;
        }}
        .cta-group {{
            flex-direction: column;
            width: 100%;
            padding: 0 {SPACING['4']};
        }}
        .stButton {{
            width: 100% !important;
        }}
        .stButton > button {{
            width: 100% !important;
        }}
    }}

    /* Accessibility Focus States */
    .stButton > button:focus {{
        outline: 2px solid {COLORS['accent_blue']};
        outline-offset: 2px;
    }}
</style>
""", unsafe_allow_html=True)

# Hero Section Layout
with st.container():
    st.markdown("""
        <div class="hero-container">
            <div class="orb-1"></div>
            <div class="orb-2"></div>
            <div class="hero-content">
                <p class="eyebrow">EDUMIND AI</p>
                <h2 class="headline">Learn Smarter. Not Harder.</h2>
                <div class="subheadline">
                    The world's most intuitive AI learning companion. <br>
                    Upload your study materials and watch them transform into 
                    personalized interactive lessons tailored just for you.
                </div>
                <div id="cta-placeholder" style="height: 0px;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# CTA Buttons positioned absolutely over the placeholder or just after the container
# We'll use a negative margin trick to pull them into the hero section if needed, 
# but simple columns after the absolute-height hero is also an option.
# Since hero-container is min-height 100vh, we should probably put them INSIDE or use negative margin.
# Actually, I'll make the hero-container a bit smaller or more flexible.
# Let's just use columns and style them into the layout.

st.markdown('<div class="cta-group-wrapper" style="margin-top: -20px; padding-bottom: 60px; position: relative; z-index: 10;">', unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 2, 1])

with col3:
    if st.button("Get Started", key="btn_signup", use_container_width=True):
        st.switch_page("pages/signup.py")

with col4:
    if st.button("Log In", key="btn_login", use_container_width=True):
        st.switch_page("pages/login.py")
st.markdown('</div>', unsafe_allow_html=True)

# Custom CSS for buttons and cta-group
st.markdown(f"""
<style>
    .cta-group-wrapper {{
        opacity: 0;
        animation: fadeIn 0.8s ease-out 0.4s forwards;
    }}
    
    /* Primary Button Style */
    div[data-testid="stButton"] button[key="btn_signup"] {{
        background: linear-gradient(135deg, {COLORS['accent_blue']}, {COLORS['accent_blue_hover']}) !important;
        color: white !important;
        padding: 20px 60px !important; /* Larger padding */
        font-size: {TYPOGRAPHY['xl']} !important; /* Larger font */
        font-weight: {FONT_WEIGHTS['bold']} !important;
        border-radius: {RADIUS['xl']} !important;
        box-shadow: {SHADOWS['glow_blue']} !important;
        border: none !important;
        height: auto !important;
        transition: all {TRANSITIONS['normal']} !important;
    }}

    /* Secondary Button Style */
    div[data-testid="stButton"] button[key="btn_login"] {{
        background: transparent !important;
        border: 2px solid {COLORS['border_default']} !important;
        color: {COLORS['text_secondary']} !important;
        padding: 18px 60px !important; /* Matched padding */
        font-size: {TYPOGRAPHY['xl']} !important; /* Matched font */
        border-radius: {RADIUS['xl']} !important;
        box-shadow: none !important;
        height: auto !important;
        transition: all {TRANSITIONS['normal']} !important;
    }}
    
    div[data-testid="stButton"] button[key="btn_login"]:hover {{
        border-color: {COLORS['accent_blue']} !important;
        color: {COLORS['text_primary']} !important;
    }}
</style>
""", unsafe_allow_html=True)

# Feature Cards Section
st.markdown(f"""
<div style="max-width: 1200px; margin: {SPACING['12']} auto; padding: 0 {SPACING['6']};">
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: {SPACING['4']};">
        <!-- Feature 1 -->
        <div class="feature-card">
            <div class="feature-icon">📂</div>
            <h3 class="feature-title">Instant Knowledge</h3>
            <p class="feature-desc">Drop any PDF and our neural engine processes thousands of pages in seconds, ready for your questions.</p>
        </div>
        <!-- Feature 2 -->
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <h3 class="feature-title">Deep Dialogue</h3>
            <p class="feature-desc">Engage in meaningful conversations with your materials. AI tutors guide you through complex concepts.</p>
        </div>
        <!-- Feature 3 -->
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <h3 class="feature-title">Progress Sync</h3>
            <p class="feature-desc">Your learning journey is mapped. Track mastery over topics and visualize your academic growth over time.</p>
        </div>
        <!-- Feature 4 -->
        <div class="feature-card">
            <div class="feature-icon">📅</div>
            <h3 class="feature-title">AI Study Planner</h3>
            <p class="feature-desc">Upload your PDF and our AI AGENT will help you generate a personalized study timetable. Get notified of your plan, which plays a vital role in organizing your academic success.</p>
        </div>
    </div>
</div>
<style>
    .feature-card {{
        background: {COLORS['bg_secondary']};
        border: 1px solid {COLORS['border_default']};
        border-radius: {RADIUS['lg']};
        padding: {SPACING['4']};
        transition: all {TRANSITIONS['normal']};
        opacity: 0;
        animation: fadeIn 0.8s ease-out 0.6s forwards;
    }}
    .feature-card:hover {{
        transform: translateY(-5px);
        border-color: {COLORS['accent_blue']};
        box-shadow: {SHADOWS['lg']};
    }}
    .feature-icon {{
        width: 48px;
        height: 48px;
        background: {COLORS['accent_blue_light']};
        border-radius: {RADIUS['md']};
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: {SPACING['3']};
        border: 1px solid {COLORS['accent_blue_light']};
    }}
    .feature-title {{
        font-size: {TYPOGRAPHY['xl']};
        margin-bottom: {SPACING['2']};
        color: {COLORS['text_primary']};
        font-weight: {FONT_WEIGHTS['semibold']};
    }}
    .feature-desc {{
        color: {COLORS['text_secondary']};
        line-height: 1.6;
        font-size: {TYPOGRAPHY['base']};
    }}
</style>
""", unsafe_allow_html=True)

# Premium Footer
st.markdown(f"""
<footer style="background-color: {COLORS['bg_secondary']}; border-top: 1px solid {COLORS['border_default']}; padding: {SPACING['10']} 0 {SPACING['6']} 0; margin-top: {SPACING['12']};">
    <div style="max-width: 1200px; margin: 0 auto; padding: 0 {SPACING['6']};">
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: {SPACING['6']}; margin-bottom: {SPACING['8']};">
            <div style="flex: 1; min-width: 250px;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: {SPACING['4']};">
                    <span style="font-size: 1.5rem;">🎓</span>
                    <span style="font-weight: bold; font-size: 1.2rem; color: {COLORS['text_primary']}; text-transform: uppercase; letter-spacing: 1px;">EduMind AI</span>
                </div>
                <p style="color: {COLORS['text_secondary']}; line-height: 1.6; font-size: {TYPOGRAPHY['sm']};">
                    Empowering students globally with cutting-edge artificial intelligence. 
                    Your learning, personalized and interactive.
                </p>
            </div>
            <div style="display: flex; gap: {SPACING['10']};">
                <div>
                    <h4 style="color: {COLORS['text_primary']}; font-size: {TYPOGRAPHY['sm']}; margin-bottom: {SPACING['4']}; text-transform: uppercase; letter-spacing: 1px;">Platform</h4>
                    <ul style="list-style: none; padding: 0; margin: 0; line-height: 2;">
                        <li><a href="#" style="color: {COLORS['text_secondary']}; text-decoration: none; font-size: {TYPOGRAPHY['sm']}; transition: color 0.2s;">Features</a></li>
                        <li><a href="#" style="color: {COLORS['text_secondary']}; text-decoration: none; font-size: {TYPOGRAPHY['sm']}; transition: color 0.2s;">Solutions</a></li>
                        <li><a href="#" style="color: {COLORS['text_secondary']}; text-decoration: none; font-size: {TYPOGRAPHY['sm']}; transition: color 0.2s;">Updates</a></li>
                    </ul>
                </div>
                <div>
                    <h4 style="color: {COLORS['text_primary']}; font-size: {TYPOGRAPHY['sm']}; margin-bottom: {SPACING['4']}; text-transform: uppercase; letter-spacing: 1px;">Company</h4>
                    <ul style="list-style: none; padding: 0; margin: 0; line-height: 2;">
                        <li><a href="#" style="color: {COLORS['text_secondary']}; text-decoration: none; font-size: {TYPOGRAPHY['sm']}; transition: color 0.2s;">About Us</a></li>
                        <li><a href="#" style="color: {COLORS['text_secondary']}; text-decoration: none; font-size: {TYPOGRAPHY['sm']}; transition: color 0.2s;">Contact</a></li>
                        <li><a href="#" style="color: {COLORS['text_secondary']}; text-decoration: none; font-size: {TYPOGRAPHY['sm']}; transition: color 0.2s;">Privacy</a></li>
                    </ul>
                </div>
            </div>
        </div>
        <div style="border-top: 1px solid {COLORS['border_subtle']}; padding-top: {SPACING['6']}; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: {SPACING['4']}; position: relative; z-index: 1;">
            <p style="color: {COLORS['text_tertiary']}; font-size: 11px; margin: 0;">
                © 2026 EduMind AI Learning Systems. All rights reserved.
            </p>
            <div style="display: flex; gap: {SPACING['4']};">
                <span style="color: {COLORS['text_tertiary']}; font-size: 11px; cursor: pointer;">Twitter</span>
                <span style="color: {COLORS['text_tertiary']}; font-size: 11px; cursor: pointer;">GitHub</span>
                <span style="color: {COLORS['text_tertiary']}; font-size: 11px; cursor: pointer;">LinkedIn</span>
            </div>
        </div>
    </div>
</footer>
<div style="height: 100px;"></div>
""", unsafe_allow_html=True)
