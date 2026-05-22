import streamlit as st
import requests
import time
import pandas as pd
import plotly.graph_objects as go
from design_system import *

# Page Config
st.set_page_config(
    page_title="EduMind | Mastery Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Global CSS
inject_custom_css()

# Custom Progress CSS
st.markdown(f"""
<style>
    /* Metric Card Customization */
    .progress-metric-card {{
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 32px;
        text-align: center;
        height: 100%;
    }}
    .p-metric-label {{
        font-size: 12px;
        text-transform: uppercase;
        color: #9ca3af;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
    }}
    .p-metric-value {{
        font-size: 48px;
        font-weight: bold;
        color: #f9fafb;
    }}
    .p-metric-subtitle {{
        font-size: 14px;
        color: #9ca3af;
        margin-top: 4px;
    }}

    /* Section Titles */
    .chart-title {{
        font-size: 24px;
        font-weight: bold;
        color: #f9fafb;
        margin: 40px 0 24px 0;
    }}

    /* Weak Area Cards */
    .weak-card {{
        background-color: #1f2937;
        border-left: 4px solid #ef4444;
        border-top: 1px solid #374151;
        border-right: 1px solid #374151;
        border-bottom: 1px solid #374151;
        padding: 24px;
        border-radius: 4px 8px 8px 4px;
        margin-bottom: 16px;
    }}
    .weak-title {{
        font-size: 20px;
        font-weight: bold;
        color: #f9fafb;
        margin-bottom: 8px;
    }}
    .weak-score {{
        font-size: 36px;
        color: #ef4444;
        font-weight: bold;
        margin-bottom: 4px;
    }}
    .weak-msg {{
        font-size: 14px;
        color: #9ca3af;
        margin-bottom: 16px;
    }}

    /* Recommendation Cards */
    .rec-card {{
        background-color: #1f2937;
        border: 1px solid #3b82f6;
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 16px;
        display: flex;
        flex-direction: column;
        gap: 12px;
    }}
    .rec-text {{
        font-size: 16px;
        color: #f9fafb;
        line-height: 1.5;
    }}
</style>
""", unsafe_allow_html=True)

# Auth Check
if 'jwt_token' not in st.session_state:
    st.switch_page('pages/login.py')

API_BASE = "http://localhost:6000/api"
headers = {"Authorization": f"Bearer {st.session_state.jwt_token}"}

# --- Data Fetching ---
@st.cache_data(ttl=300)
def fetch_progress_data():
    try:
        res = requests.get(f"{API_BASE}/student/progress", headers=headers, timeout=10)
        return res.json() if res.status_code == 200 else {}
    except:
        return {}

@st.cache_data(ttl=300)
def fetch_quiz_history():
    try:
        res = requests.get(f"{API_BASE}/student/quiz-history", headers=headers, timeout=10)
        return res.json() if res.status_code == 200 else []
    except:
        return []

@st.cache_data(ttl=300)
def fetch_topic_scores():
    try:
        res = requests.get(f"{API_BASE}/student/topic-scores", headers=headers, timeout=10)
        return res.json() if res.status_code == 200 else []
    except:
        return []

@st.cache_data(ttl=600)
def fetch_recommendations():
    try:
        res = requests.post(f"{API_BASE}/student/get-recommendations", headers=headers, timeout=30)
        return res.json().get("recommendations", []) if res.status_code == 200 else []
    except:
        return []

# Load Data
progress = fetch_progress_data()
history = fetch_quiz_history()
topic_scores = fetch_topic_scores()
recommendations = fetch_recommendations()

# --- Header ---
st.markdown("""
<div style="margin-bottom: 40px;">
    <div style="font-size: 32px; font-weight: bold; color: #f9fafb; margin-bottom: 8px;">Mastery Analytics</div>
    <div style="font-size: 16px; color: #9ca3af;">Visual telemetry for your academic performance and conceptual trajectory.</div>
</div>
""", unsafe_allow_html=True)

# --- TOP METRICS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="progress-metric-card">
            <div class="p-metric-label">⚡ FOCUS VELOCITY</div>
            <div class="p-metric-value">{progress.get('study_hours', 0)}h</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="progress-metric-card">
            <div class="p-metric-label">🔥 CONSISTENCY</div>
            <div class="p-metric-value">{progress.get('streak', 0)}</div>
            <div class="p-metric-subtitle">day streak</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    avg_m = float(progress.get('avg_score', 0))
    color = "#10b981" if avg_m > 70 else "#f59e0b" if avg_m >= 50 else "#ef4444"
    st.markdown(f"""
        <div class="progress-metric-card">
            <div class="p-metric-label">🎯 AVG MASTERY</div>
            <div class="p-metric-value" style="color: {color};">{avg_m}%</div>
        </div>
    """, unsafe_allow_html=True)

# --- CHART 1: SYSTEM MASTERY TREND ---
st.markdown('<div class="chart-title">System Mastery Trend</div>', unsafe_allow_html=True)

if history:
    df_hist = pd.DataFrame(history)
    df_hist['date'] = pd.to_datetime(df_hist['date'])
    df_hist = df_hist.sort_values('date')
    
    # Scale score to percentage if it's 1-5
    df_hist['display_score'] = df_hist['score'] * 20 if df_hist['score'].max() <= 5 else df_hist['score']

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=df_hist['date'],
        y=df_hist['display_score'],
        mode='lines+markers',
        line=dict(color='#3b82f6', width=3),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.1)',
        marker=dict(size=8, color='#3b82f6', line=dict(width=2, color='#f9fafb'))
    ))
    fig_line.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f9fafb'),
        xaxis=dict(showgrid=True, gridcolor='#374151', title="Assessment Date"),
        yaxis=dict(showgrid=True, gridcolor='#374151', range=[0, 105], title="Mastery %"),
        margin=dict(l=0, r=0, t=20, b=0),
        height=400,
        hovermode="x unified"
    )
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("Complete assessments to see your mastery trend.")

# --- CHART 2: PERFORMANCE BY TOPIC ---
st.markdown('<div class="chart-title">Performance by Topic</div>', unsafe_allow_html=True)

if topic_scores:
    # Scale scores if needed (assuming backend returns scale 1-5 or 0-100)
    for t in topic_scores:
        t['avg_score'] = float(t.get('avg_score', 0))
        if t['avg_score'] <= 5: t['avg_score'] *= 20
        
    df_topics = pd.DataFrame(topic_scores)
    
    # Assign colors
    colors = []
    for s in df_topics['avg_score']:
        if s > 80: colors.append('#10b981')
        elif s >= 60: colors.append('#f59e0b')
        else: colors.append('#ef4444')
    
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        y=df_topics['topic'],
        x=df_topics['avg_score'],
        orientation='h',
        marker_color=colors,
        text=df_topics['avg_score'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside',
        textfont=dict(color='#f9fafb')
    ))
    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f9fafb'),
        xaxis=dict(showgrid=True, gridcolor='#374151', range=[0, 115], title="Avg Score"),
        yaxis=dict(showgrid=False),
        margin=dict(l=0, r=0, t=20, b=0),
        height=300 + (len(topic_scores) * 30),
    )
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("Topic-specific analytics will appear as you progress.")

# --- WEAK AREAS ---
st.markdown('<div class="chart-title">Areas Requiring Focus</div>', unsafe_allow_html=True)

weak_areas = [t for t in topic_scores if t['avg_score'] < 70]

if weak_areas:
    for area in weak_areas:
        st.markdown(f"""
            <div class="weak-card">
                <div class="weak-title">{area['topic']}</div>
                <div class="weak-score">{area['avg_score']:.1f}%</div>
                <div class="weak-msg">Recommended: Review this topic thoroughly to reinforce core concepts.</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"Start Review: {area['topic']}", key=f"rev_{area['topic']}"):
            st.switch_page("pages/chat.py")
else:
    st.markdown("""
        <div style="background-color: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; border-radius: 8px; padding: 24px; text-align: center; color: #10b981; font-weight: 600;">
            🎉 All topics mastered! Keep maintaining your current study rhythm.
        </div>
    """, unsafe_allow_html=True)

# --- RECOMMENDATIONS ---
st.markdown('<div class="chart-title">AI Recommendations</div>', unsafe_allow_html=True)

if recommendations:
    for rec in recommendations:
        st.markdown(f"""
            <div class="rec-card">
                <div class="rec-text">💡 {rec}</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Take Action", key=f"act_{rec[:20]}"):
            st.switch_page("pages/dashboard.py")
else:
    st.markdown("""
        <div style="color: #9ca3af; font-style: italic;">
            System analyzing performance logs... New recommendations will appear shortly.
        </div>
    """, unsafe_allow_html=True)
