import streamlit as st
import requests
import time
import json
from design_system import *

# Page Config
st.set_page_config(
    page_title="EduMind | AI Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Global CSS
inject_custom_css()

# Custom Chat CSS
st.markdown(f"""
<style>
    /* Main Layout Overrides */
    .stApp {{
        background-color: #0f1419;
    }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: #1f2937 !important;
        border-right: 1px solid #374151 !important;
    }}
    
    /* Sidebar Content */
    .sidebar-title {{
        font-size: 20px;
        font-weight: bold;
        color: #f9fafb;
        margin-bottom: 8px;
    }}
    .sidebar-status {{
        font-size: 12px;
        color: #9ca3af;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    .status-dot {{
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
    }}

    /* Session Controls */
    .stButton button {{
        border-radius: 8px !important;
        font-size: 14px !important;
        padding: 8px 16px !important;
    }}

    /* History List */
    .history-container {{
        margin-top: 32px;
    }}
    .history-item {{
        padding: 12px;
        border-radius: 8px;
        font-size: 14px;
        color: #9ca3af;
        cursor: pointer;
        transition: all 0.2s;
        margin-bottom: 4px;
    }}
    .history-item:hover {{
        background-color: #374151;
        color: #f9fafb;
    }}

    /* Chat Area */
    .chat-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 0;
        border-bottom: 1px solid #374151;
        margin-bottom: 24px;
    }}
    .live-badge {{
        background-color: rgba(16, 185, 129, 0.1);
        color: #10b981;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }}

    /* Message Bubbles */
    .message-container {{
        display: flex;
        flex-direction: column;
        gap: 16px;
        padding-bottom: 100px;
    }}

    .user-bubble {{
        background-color: #3b82f6;
        color: white;
        max-width: 70%;
        margin-left: auto;
        border-radius: 16px 16px 4px 16px;
        padding: 12px 16px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
        font-size: 15px;
        line-height: 1.5;
    }}

    .ai-bubble-wrapper {{
        width: 100%;
        margin-bottom: 8px;
    }}
    .ai-label {{
        font-size: 11px;
        font-weight: 700;
        color: #3b82f6;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .ai-bubble {{
        background-color: #1f2937;
        color: #f9fafb;
        max-width: 75%;
        margin-right: auto;
        border-radius: 16px 16px 16px 4px;
        border: 1px solid #374151;
        padding: 16px;
        font-size: 15px;
        line-height: 1.6;
    }}

    /* Typing Indicator */
    @keyframes bounce {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-4px); }}
    }}
    .typing-indicator {{
        display: flex;
        gap: 4px;
        padding: 12px 16px;
        background: #1f2937;
        border-radius: 12px;
        width: fit-content;
        margin-bottom: 16px;
    }}
    .dot {{
        width: 6px;
        height: 6px;
        background: #3b82f6;
        border-radius: 50%;
        animation: bounce 1s infinite;
    }}

    /* Chat Input Fixed */
    .input-container {{
        position: fixed;
        bottom: 30px;
        padding: 0 20px;
        z-index: 100;
    }}
    /* Standard streamlit input styling override */
    .stTextInput > div > div > input {{
        background-color: #1f2937 !important;
        border: 2px solid #374151 !important;
        border-radius: 12px !important;
        color: #f9fafb !important;
        padding: 14px 20px !important;
        font-size: 16px !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1) !important;
    }}

    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: transparent;
    }}
    ::-webkit-scrollbar-thumb {{
        background: #374151;
        border-radius: 10px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: #4b5563;
    }}
</style>
""", unsafe_allow_html=True)

# Auth Check
if 'jwt_token' not in st.session_state:
    st.switch_page('pages/login.py')

# Initialize Session State
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chat_history_list' not in st.session_state:
    st.session_state.chat_history_list = [
        {"topic": "Quantum Computing Basics", "date": "Oct 24"},
        {"topic": "Neural Network Architecture", "date": "Oct 22"},
        {"topic": "Data Structures in Python", "date": "Oct 20"}
    ]

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-title">AI Academic Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-status"><div class="status-dot"></div>System Status: Operational • v2.0</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✨ New Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
            
    if st.button("📥 Export Chat", use_container_width=True):
        chat_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        st.download_button("Download Transcript", data=chat_text, file_name="chat_export.txt")

    st.markdown('<div class="history-container">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 12px; color: #6b7280; font-weight: bold; margin-bottom: 12px; text-transform: uppercase;">Recent Conversations</div>', unsafe_allow_html=True)
    for chat in st.session_state.chat_history_list:
        st.markdown(f'<div class="history-item"><b>{chat["topic"]}</b><br><span style="font-size: 11px;">{chat["date"]}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Main Chat Area
st.markdown("""
<div class="chat-header">
    <div>
        <div style="font-size: 24px; font-weight: bold; color: #f9fafb;">AI Academic Assistant</div>
        <div style="font-size: 14px; color: #9ca3af;">Personalized Neural Tutor Agent</div>
    </div>
    <div class="live-badge">🟢 LIVE SESSION</div>
</div>
""", unsafe_allow_html=True)

# Messages Container
message_container = st.container()

with message_container:
    st.markdown('<div class="message-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="ai-bubble-wrapper">
                    <div class="ai-label">AI ASSISTANT</div>
                    <div class="ai-bubble">{msg["content"]}</div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Chat Input Logic
input_placeholder = "Query the system..."
user_input = st.chat_input(input_placeholder)

if user_input:
    # 1. Add User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()

# Processing AI Response (if last message is user)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with message_container:
        # Show Typing Indicator
        typing_placeholder = st.empty()
        typing_placeholder.markdown("""
            <div class="typing-indicator">
                <div class="dot" style="animation-delay: 0s"></div>
                <div class="dot" style="animation-delay: 0.2s"></div>
                <div class="dot" style="animation-delay: 0.4s"></div>
            </div>
        """, unsafe_allow_html=True)
        
        # 2. Call API
        try:
            token = st.session_state.jwt_token
            api_url = "http://localhost:6000/api/ai/chat"
            payload = {
                "message": st.session_state.messages[-1]["content"],
                "history": st.session_state.messages[:-1]
            }
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            
            typing_placeholder.empty()
            
            if response.status_code == 200:
                full_response = response.json().get("response", "No response received.")
                
                # 3. Stream Response (Simulated word by word)
                ai_msg_placeholder = st.empty()
                curr_text = ""
                words = full_response.split()
                
                for word in words:
                    curr_text += word + " "
                    ai_msg_placeholder.markdown(f"""
                        <div class="ai-bubble-wrapper">
                            <div class="ai-label">AI ASSISTANT</div>
                            <div class="ai-bubble">{curr_text}▌</div>
                        </div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.05)
                
                ai_msg_placeholder.markdown(f"""
                    <div class="ai-bubble-wrapper">
                        <div class="ai-label">AI ASSISTANT</div>
                        <div class="ai-bubble">{curr_text}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.session_state.messages.append({"role": "assistant", "content": curr_text.strip()})
                
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
                st.session_state.messages.append({"role": "assistant", "content": "I apologize, but I encountered an error processing your request. Please try again."})
                
        except Exception as e:
            typing_placeholder.empty()
            st.error(f"Connection error: {str(e)}")
            st.session_state.messages.append({"role": "assistant", "content": "The neural system is currently unreachable. Please ensure the backend is active."})
        
        st.rerun()
