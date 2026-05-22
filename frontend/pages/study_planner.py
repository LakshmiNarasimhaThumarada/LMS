import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import List, Dict
import sys
import os

# Add root directory to path to import design_system
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import design system
try:
    from design_system import *
    inject_custom_css()
except ImportError:
    st.warning("Design system not found. Using default styles.")
    def inject_custom_css(): pass

# Configuration
BACKEND_URL = st.secrets.get('BACKEND_URL', 'http://localhost:8000')

def check_auth():
    """Check if user is authenticated"""
    if 'jwt_token' not in st.session_state:
        # For development/demo purposes, we might want a fallback or clear message
        if 'user' in st.session_state and st.session_state.get('jwt_token'):
            return
        st.warning("⛔ Please log in first to access the AI Study Planner.")
        if st.button("Go to Login"):
            st.switch_page("EduMind.py") # Assuming root is EduMind.py
        st.stop()

def api_call(endpoint: str, method: str = 'GET', data: dict = None, files: dict = None):
    """Make API call with JWT authentication"""
    
    headers = {}
    if 'jwt_token' in st.session_state:
        headers['Authorization'] = f"Bearer {st.session_state['jwt_token']}"
    
    url = f"{BACKEND_URL}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            if files:
                response = requests.post(url, headers=headers, files=files)
            else:
                headers['Content-Type'] = 'application/json'
                response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            headers['Content-Type'] = 'application/json'
            response = requests.put(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            try:
                error_detail = response.json().get('detail', 'Unknown error')
            except:
                error_detail = f"Status Code: {response.status_code}"
            st.error(f"API Error: {error_detail}")
            return None
            
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

# Main app
check_auth()

st.title("📅 AI Study Planner")
st.markdown("Generate personalized study timetables with AI")

# Check for active plan
active_plan = api_call('/api/planner/active-plan')

if not active_plan:
    # ═══════════════════════════════════════════════════════════
    # CREATE NEW PLAN FLOW
    # ═══════════════════════════════════════════════════════════
    
    st.markdown("---")
    st.subheader("📚 Step 1: Select Study Material")
    
    # Get user's PDFs
    pdfs = api_call('/api/planner/user-pdfs')
    
    if not pdfs:
        st.info("📁 No PDFs uploaded yet. Please upload study materials first.")
        if st.button("Go to My Materials"):
            # Check if materials page exists
            st.switch_page('pages/materials.py')
        st.stop()
    
    # PDF selection
    selected_pdf = st.selectbox(
        "Choose a PDF to create study plan for:",
        options=pdfs,
        format_func=lambda x: f"{x['filename']} ({x.get('analysis', {}).get('total_topics', 0)} topics, {x.get('analysis', {}).get('estimated_hours', {}).get('total', 0)}h estimated)"
    )
    
    if selected_pdf:
        # Show PDF analysis summary
        analysis = selected_pdf.get('analysis', {})
        with st.expander("📊 PDF Analysis Summary"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Topics", analysis.get('total_topics', 0))
            with col2:
                st.metric("Difficulty", analysis.get('difficulty', 'Unknown'))
            with col3:
                st.metric("Est. Hours", f"{analysis.get('estimated_hours', {}).get('total', 0)}h")
    
    st.markdown("---")
    st.subheader("⚙️ Step 2: Set Your Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        exam_date = st.date_input(
            "📅 When is your exam?",
            min_value=datetime.now().date() + timedelta(days=1),
            value=datetime.now().date() + timedelta(days=30),
            help="The AI will create a schedule to prepare you by this date"
        )
        
        hours_per_day = st.slider(
            "⏰ Hours you can study per day:",
            min_value=0.5,
            max_value=8.0,
            value=3.0,
            step=0.5,
            help="Be realistic! Quality over quantity."
        )
        
        skip_weekends = st.checkbox(
            "Skip weekends",
            value=True,
            help="Enable study sessions on weekends too"
        )
    
    with col2:
        preferred_times = st.multiselect(
            "🕐 Preferred study times:",
            options=['morning', 'afternoon', 'evening', 'night'],
            default=['morning', 'evening'],
            help="When do you focus best?"
        )
        
        study_style = st.radio(
            "📖 Study style:",
            options=['distributed', 'intensive'],
            format_func=lambda x: {
                'distributed': '📚 Distributed (shorter sessions, better retention)',
                'intensive': '💪 Intensive (longer sessions, faster progress)'
            }[x],
            help="Distributed = 1.5h sessions. Intensive = 2.5h sessions."
        )
    
    st.markdown("---")
    
    # Generate plan
    if st.button("🎯 Generate My Study Plan", type="primary", use_container_width=True):
        with st.spinner("🤖 AI is creating your personalized study plan..."):
            
            # Call API to generate plan
            result = api_call(
                '/api/planner/generate-plan',
                method='POST',
                data={
                    'pdf_id': selected_pdf['pdf_id'],
                    'preferences': {
                        'exam_date': exam_date.strftime('%Y-%m-%d'),
                        'hours_per_day': hours_per_day,
                        'preferred_times': preferred_times,
                        'study_style': study_style,
                        'skip_weekends': skip_weekends
                    }
                }
            )
            
            if result:
                st.success("✅ Your study plan is ready!")
                st.balloons()
                st.rerun()

else:
    # ═══════════════════════════════════════════════════════════
    # ACTIVE PLAN DISPLAY
    # ═══════════════════════════════════════════════════════════
    
    plan = active_plan
    
    # Header with plan info
    st.success(f"📚 Active plan for: **{plan['pdf_filename']}**")
    st.caption(f"Created: {datetime.fromisoformat(plan['created_at'].replace('Z', '+00:00')).strftime('%B %d, %Y')}")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    summary = plan['summary']
    completed_sessions = [s for s in plan['sessions'] if s.get('completed')]
    completed_count = len(completed_sessions)
    
    with col1:
        st.metric(
            "Total Sessions",
            summary['total_sessions'],
            delta=f"{completed_count} done"
        )
    
    with col2:
        st.metric(
            "Total Hours",
            f"{summary['total_hours']}h"
        )
    
    with col3:
        progress_pct = (completed_count / summary['total_sessions'] * 100) if summary['total_sessions'] > 0 else 0
        st.metric(
            "Progress",
            f"{progress_pct:.0f}%"
        )
    
    with col4:
        st.metric(
            "Exam Date",
            datetime.strptime(summary['exam_date'], '%Y-%m-%d').strftime('%b %d')
        )
    
    # Progress bar
    st.progress(progress_pct / 100)
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📅 This Week",
        "📊 Progress",
        "🔔 Notifications",
        "⚙️ Settings"
    ])
    
    with tab1:
        # ═══ THIS WEEK VIEW ═══
        st.subheader("📅 Upcoming Sessions (Next 7 Days)")
        
        # Get upcoming sessions
        upcoming_response = api_call('/api/planner/upcoming-sessions?days=7')
        upcoming = upcoming_response if upcoming_response else []
        
        if not upcoming:
            st.info("🎉 No sessions scheduled for this week. Great job staying ahead!")
        else:
            for session in upcoming:
                date = datetime.strptime(session['date'], '%Y-%m-%d')
                is_today = date.date() == datetime.now().date()
                
                # Session card
                with st.container():
                    col1, col2, col3 = st.columns([2, 5, 2])
                    
                    with col1:
                        day_label = "🔥 TODAY" if is_today else date.strftime('%A, %b %d')
                        st.markdown(f"**{day_label}**")
                        st.caption(session['time'])
                    
                    with col2:
                        type_emoji = {
                            'study': '📖',
                            'review_1': '🔄',
                            'review_7': '✅',
                            'practice': '💪',
                            'adaptive_review': '🎯'
                        }.get(session['type'], '📚')
                        
                        st.markdown(f"{type_emoji} **{session['chapter_name']}**")
                        st.caption(f"{session.get('duration', 0)}h • {session['type'].replace('_', ' ').title()}")
                        if session.get('topics'):
                            st.caption(f"Topics: {', '.join(session['topics'][:3])}{'...' if len(session['topics']) > 3 else ''}")
                    
                    with col3:
                        if session.get('completed'):
                            st.success("✅ Done")
                        elif is_today or date.date() < datetime.now().date():
                            if st.button("Mark Complete", key=session['id']):
                                # Using a more robust session state to handle difficulty selection
                                st.session_state[f"completing_{session['id']}"] = True
                        
                        if st.session_state.get(f"completing_{session['id']}"):
                            difficulty = st.selectbox(
                                "Difficulty?",
                                options=['easy', 'medium', 'hard'],
                                key=f"diff_sel_{session['id']}"
                            )
                            
                            if st.button("Confirm", key=f"conf_{session['id']}"):
                                result = api_call(
                                    '/api/progress/complete-session',
                                    method='POST',
                                    data={
                                        'session_id': session['id'],
                                        'completed': True,
                                        'difficulty_rating': difficulty
                                    }
                                )
                                
                                if result:
                                    if difficulty == 'hard':
                                        st.success("✅ Done! Extra review added.")
                                    else:
                                        st.success("✅ Done!")
                                    st.session_state[f"completing_{session['id']}"] = False
                                    st.rerun()
                    
                    st.markdown("---")
    
    with tab2:
        # ═══ PROGRESS VIEW ═══
        st.subheader("📊 Your Progress")
        
        # Get detailed stats
        stats = api_call('/api/progress/stats')
        
        if stats:
            # Metrics row
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "⚡ Study Velocity",
                    f"{stats.get('total_hours_studied', 0)}h",
                    delta="Total time"
                )
            
            with col2:
                st.metric(
                    "🔥 Streak",
                    f"{stats.get('current_streak', 0)} days",
                    delta="Keep it up!"
                )
            
            with col3:
                st.metric(
                    "✅ Completion",
                    f"{stats.get('completion_rate', 0)}%",
                    delta=f"{stats.get('completed_sessions', 0)}/{stats.get('total_sessions', 0)}"
                )
            
            # Weak topics alert
            if stats.get('weak_topics'):
                st.warning("⚠️ **Topics needing more attention:**")
                for topic in stats['weak_topics']:
                    st.markdown(f"- {topic}")
            
            # Progress chart
            if stats.get('completed_sessions', 0) > 0:
                st.markdown("### 📈 Session Completion Over Time")
                
                # In a real app, we'd fetch this from backend. 
                # For now using a trend based on total completed
                dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(14, -1, -1)]
                # Simple linear trend for visualization
                completions = []
                current = 0
                step = stats['completed_sessions'] / 15
                for i in range(15):
                    current += step
                    completions.append(int(current))
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=completions,
                    mode='lines+markers',
                    fill='tozeroy',
                    line=dict(color='#3b82f6', width=3),
                    marker=dict(size=8)
                ))
                
                fig.update_layout(
                    plot_bgcolor='#1f2937',
                    paper_bgcolor='#1f2937',
                    font=dict(color='#f9fafb'),
                    xaxis=dict(showgrid=True, gridcolor='#374151'),
                    yaxis=dict(showgrid=True, gridcolor='#374151', title='Sessions Completed'),
                    margin=dict(l=0, r=0, t=20, b=0),
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # ═══ NOTIFICATIONS VIEW ═══
        st.subheader("🔔 Notification Settings")
        
        # Get current preferences
        notif_prefs = api_call('/api/notifications/preferences')
        
        if notif_prefs:
            st.markdown("### Channels")
            
            push_enabled = st.checkbox(
                "📱 Browser Push Notifications",
                value=notif_prefs.get('push_enabled', False),
                help="Get reminders in your browser"
            )
            
            email_enabled = st.checkbox(
                "📧 Email Reminders",
                value=notif_prefs.get('email_enabled', True),
                help="Get reminders via email"
            )
            
            sms_enabled = st.checkbox(
                "💬 SMS Alerts (Premium)",
                value=notif_prefs.get('sms_enabled', False),
                help="Get text message reminders",
                disabled=True  # Premium feature
            )
            
            st.markdown("### Timing")
            
            reminder_minutes = st.slider(
                "⏰ Send reminders before session:",
                min_value=5,
                max_value=60,
                value=notif_prefs.get('reminder_minutes', 15),
                step=5,
                help="Minutes before session starts"
            )
            
            if st.button("💾 Save Notification Settings"):
                result = api_call(
                    '/api/notifications/preferences',
                    method='PUT',
                    data={
                        'push_enabled': push_enabled,
                        'email_enabled': email_enabled,
                        'sms_enabled': sms_enabled,
                        'reminder_minutes': reminder_minutes
                    }
                )
                
                if result:
                    st.success("✅ Notification settings saved!")
        
        st.markdown("---")
        st.markdown("### 📆 Calendar Sync")
        
        # Calendar status
        calendar_status = api_call('/api/calendar/status')
        
        if calendar_status:
            col1, col2 = st.columns(2)
            
            with col1:
                if calendar_status.get('google_connected'):
                    st.success("✅ Google Calendar Connected")
                else:
                    if st.button("Connect Google Calendar"):
                        auth = api_call('/api/calendar/google/authorize')
                        if auth:
                            st.markdown(f"[Authorize Google Calendar]({auth['authorization_url']})")
            
            with col2:
                if calendar_status.get('microsoft_connected'):
                    st.success("✅ Outlook Connected")
                else:
                    st.info("📅 Outlook sync coming soon")
            
            if calendar_status.get('google_connected') or calendar_status.get('microsoft_connected'):
                if st.button("🔄 Sync Plan to Calendar"):
                    provider = 'google' if calendar_status.get('google_connected') else 'microsoft'
                    sync_res = api_call(f'/api/calendar/sync-plan/{plan["plan_id"]}?provider={provider}', method='POST')
                    if sync_res:
                        st.success(f"Successfully synced {sync_res['events_created']} events to your calendar!")
    
    with tab4:
        # ═══ SETTINGS VIEW ═══
        st.subheader("⚙️ Plan Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if plan.get('status') == 'active':
                if st.button("⏸️ Pause Plan", use_container_width=True):
                    result = api_call(f'/api/planner/plan/{plan["plan_id"]}/pause', method='PUT')
                    if result:
                        st.success("Plan paused")
                        st.rerun()
            else:
                if st.button("▶️ Resume Plan", use_container_width=True):
                    result = api_call(f'/api/planner/plan/{plan["plan_id"]}/resume', method='PUT')
                    if result:
                        st.success("Plan resumed")
                        st.rerun()
        
        with col2:
            if st.button("🔄 Regenerate Plan", use_container_width=True):
                st.warning("This will replace your current schedule. Are you sure?")
                if st.button("Confirm Regeneration"):
                     # Trigger regeneration logic if available or just delete and redirect
                     pass
        
        st.markdown("---")
        
        st.markdown("### ⚠️ Danger Zone")
        with st.expander("Delete Current Plan"):
            st.write("Deleting your plan will remove all scheduled sessions.")
            if st.button("🗑️ Delete Everything", type="secondary"):
                # Call delete API
                st.error("Delete functionality called. (Simulated)")
