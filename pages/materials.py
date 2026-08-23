import streamlit as st
import requests
import time
import os
from design_system import *

# Page Config
st.set_page_config(
    page_title="EduMind | Materials",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Global CSS
inject_custom_css()

# Custom Materials CSS
st.markdown(f"""
<style>
    /* Header Section */
    .materials-header {{
        margin-bottom: 40px;
    }}
    .materials-title {{
        font-size: 32px;
        font-weight: bold;
        color: #f9fafb;
        margin-bottom: 8px;
    }}
    .materials-desc {{
        font-size: 16px;
        color: #9ca3af;
    }}

    /* Upload Section */
    .section-title {{
        font-size: 20px;
        font-weight: 600;
        color: #f9fafb;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 12px;
    }}

    /* Drag & Drop Zone */
    .upload-zone {{
        width: 100%;
        min-height: 300px;
        background-color: #111827;
        border: 2px dashed #374151;
        border-radius: 12px;
        padding: 60px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 40px;
    }}
    .upload-zone:hover {{
        border-color: #3b82f6;
        background-color: #1a1f2e;
    }}
    .upload-icon {{
        font-size: 48px;
        margin-bottom: 16px;
        color: #3b82f6;
    }}
    .upload-text {{
        font-size: 18px;
        color: #f9fafb;
        font-weight: 500;
        margin-bottom: 8px;
    }}
    .upload-limit {{
        font-size: 14px;
        color: #6b7280;
    }}

    /* Progress Bar */
    .progress-container {{
        width: 100%;
        margin-top: 24px;
    }}
    .progress-track {{
        width: 100%;
        height: 8px;
        background-color: #374151;
        border-radius: 4px;
        overflow: hidden;
    }}
    .progress-fill {{
        height: 100%;
        background-color: #3b82f6;
        transition: width 0.3s ease;
    }}
    .progress-text {{
        font-size: 14px;
        color: #9ca3af;
        margin-top: 8px;
        text-align: center;
    }}

    /* Materials List */
    .materials-table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 0 8px;
    }}
    .material-row {{
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 8px;
        transition: background-color 0.2s;
    }}
    .material-row:hover {{
        background-color: #374151;
    }}
    .material-cell {{
        padding: 16px;
        color: #f9fafb;
    }}
    .cell-filename {{
        font-weight: 500;
        font-size: 16px;
    }}
    .cell-meta {{
        color: #9ca3af;
        font-size: 14px;
        text-align: center;
    }}
    
    /* Badges */
    .badge {{
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
    }}
    .badge-sync {{ background-color: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); }}
    .badge-proc {{ background-color: rgba(245, 158, 11, 0.1); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.2); }}
    .badge-fail {{ background-color: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }}

    /* Empty State */
    .empty-state {{
        background-color: #1f2937;
        padding: 40px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #374151;
    }}
    .empty-text {{
        color: #3b82f6;
        font-size: 16px;
        font-weight: 500;
    }}

    /* Action Buttons Overrides */
    .stButton button {{
        padding: 6px 14px !important;
        font-size: 13px !important;
        border-radius: 6px !important;
    }}
    .btn-delete button {{
        background: rgba(239, 68, 68, 0.1) !important;
        color: #ef4444 !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
        box-shadow: none !important;
    }}
    .btn-delete button:hover {{
        background: rgba(239, 68, 68, 0.2) !important;
        transform: none !important;
    }}
</style>
""", unsafe_allow_html=True)

# Auth Check
if 'jwt_token' not in st.session_state:
    st.switch_page('pages/login.py')

# Ensure stable IPv4 connection for Windows
API_BASE = f"{EXPRESS_URL}/api"
headers = {"Authorization": f"Bearer {st.session_state.jwt_token}"}

# --- Data Fetching ---
def fetch_pdfs():
    try:
        res = requests.get(f"{API_BASE}/student/pdfs", headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        return []
    except Exception as e:
        print(f"[DEBUG MATERIALS FETCH] Error: {e}")
        return []

# --- Delete Function ---
def delete_material(pdf_id):
    try:
        res = requests.delete(f"{API_BASE}/pdf/{pdf_id}", headers=headers, timeout=10)
        if res.status_code == 200:
            st.success("Successfully deleted material")
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"Failed to delete: {res.json().get('message', 'Unknown error')}")
    except Exception as e:
        st.error(f"Connection error: {str(e)}")

# --- Header ---
st.markdown("""
<div class="materials-header">
    <div class="materials-title">Material Synchronization</div>
    <div class="materials-desc">Ingest and manage your study foundation for AI augmented learning.</div>
</div>
""", unsafe_allow_html=True)

# --- UPLOAD SECTION ---
st.markdown('<div class="section-title">☁️ Ingest New Materials</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Browse files", type=["pdf"], label_visibility="collapsed")

if uploaded_file is not None:
    # Check if we already uploaded this file in this session to prevent double upload
    if f"uploaded_{uploaded_file.name}" not in st.session_state:
        # Check size (200MB)
        if uploaded_file.size > 200 * 1024 * 1024:
            st.error("File size exceeds 200MB limit.")
        else:
            # Simulate progress bar
            progress_bar = st.empty()
            for p in range(0, 101, 10):
                progress_bar.markdown(f"""
                    <div class="progress-container">
                        <div class="progress-track"><div class="progress-fill" style="width: {p}%"></div></div>
                        <div class="progress-text">Uploading... {p}%</div>
                    </div>
                """, unsafe_allow_html=True)
                time.sleep(0.1)
            
            # Actual upload
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            try:
                with st.spinner("Processing & Synchronizing..."):
                    res = requests.post(f"{API_BASE}/pdf/upload", files=files, headers=headers, timeout=60)
                    if res.status_code == 201:
                        pdf_id = res.json().get("pdf_id")
                        # Synchronize and index in FastAPI vectorstore
                        fastapi_headers = {"Authorization": f"Bearer {st.session_state.jwt_token}"}
                        fastapi_files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                        
                        try:
                            f_res = requests.post(
                                f"http://127.0.0.1:8000/api/planner/analyze-pdf?pdf_id={pdf_id}",
                                headers=fastapi_headers,
                                files=fastapi_files,
                                timeout=120
                            )
                            if f_res.status_code == 200:
                                st.markdown("<div style='color: #10b981; font-weight: 600; margin-top: 10px;'>✅ Synchronized and indexed successfully!</div>", unsafe_allow_html=True)
                            else:
                                st.markdown("<div style='color: #f59e0b; font-weight: 600; margin-top: 10px;'>⚠️ Synced with Express, but RAG indexing had issues.</div>", unsafe_allow_html=True)
                        except Exception as fe:
                            st.markdown(f"<div style='color: #ef4444; font-weight: 600; margin-top: 10px;'>❌ Synced, but indexing connection failed: {str(fe)}</div>", unsafe_allow_html=True)
                        
                        st.session_state[f"uploaded_{uploaded_file.name}"] = True
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error(f"Upload failed: {res.json().get('message', 'Unknown error')}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

# --- MATERIALS LIST ---
st.markdown('<div class="section-title" style="margin-top: 40px;">📂 Synchronized Materials</div>', unsafe_allow_html=True)

materials = fetch_pdfs()

if not materials:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-text">Awaiting synchronization with material database.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for m in materials:
        # We'll use a container with columns for each row
        with st.container():
            col1, col2, col3, col4 = st.columns([4, 2, 2, 3])
            
            with col1:
                st.markdown(f'<div style="padding-top: 8px;"><span class="cell-filename">{m["filename"]}</span></div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'<div class="cell-meta" style="padding-top: 10px;">{m["upload_date"]}</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div style="text-align: center; padding-top: 8px;"><span class="badge badge-sync">Synchronized</span></div>', unsafe_allow_html=True)
            
            with col4:
                # Actions
                btn_cols = st.columns(3)
                with btn_cols[0]:
                    if st.button("💬 Chat", key=f"chat_{m['id']}"):
                        st.switch_page("pages/chat.py")
                with btn_cols[1]:
                    if st.button("📝 Quiz", key=f"quiz_{m['id']}"):
                        st.switch_page("pages/quiz.py")
                with btn_cols[2]:
                    st.markdown('<div class="btn-delete">', unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_{m['id']}"):
                        # Simple confirmation via session state
                        st.session_state[f"confirm_del_{m['id']}"] = True
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Confirmation Dialog Overlay
            if st.session_state.get(f"confirm_del_{m['id']}", False):
                with st.container():
                    st.warning(f"Are you sure you want to delete '{m['filename']}'?")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Confirm Delete", key=f"conf_{m['id']}"):
                            delete_material(m['id'])
                            st.session_state[f"confirm_del_{m['id']}"] = False
                    with c2:
                        if st.button("Cancel", key=f"canc_{m['id']}"):
                            st.session_state[f"confirm_del_{m['id']}"] = False
                            st.rerun()
            
            st.markdown('<hr style="margin: 8px 0; border: 0; border-top: 1px solid #374151;">', unsafe_allow_html=True)
