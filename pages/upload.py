import streamlit as st
import requests
import time
import os
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="EduMind - Material Sync",
    page_icon="📂",
    layout="wide",
)

# Authentication Check
if 'jwt_token' not in st.session_state or 'user' not in st.session_state:
    st.warning("Please login to access student materials.")
    time.sleep(1)
    st.switch_page("pages/login.py")

user = st.session_state['user']
token = st.session_state['jwt_token']
headers = {"Authorization": f"Bearer {token}"}

# --- Custom Professional Dark CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #030712;
        color: #f8fafc;
    }

    .main .block-container {
        padding: 2rem 4rem;
        max-width: 1000px;
    }

    /* Enterprise Cards */
    .upload-card {
        background: #0f172a;
        border: 1px solid rgba(30, 41, 59, 1);
        padding: 3rem;
        border-radius: 16px;
        margin-bottom: 3rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Modern Table Styling */
    .stDataFrame {
        border: 1px solid rgba(30, 41, 59, 0.5) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    /* Alerts and Badges */
    .stAlert {
        background-color: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(30, 41, 59, 0.8) !important;
        color: #f1f5f9 !important;
    }

    /* File Uploader Customization */
    [data-testid="stFileUploader"] section {
        background-color: #020617 !important;
        border: 1px dashed rgba(59, 130, 246, 0.3) !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stFileUploader"] section:hover {
        border-color: #3b82f6 !important;
        background-color: rgba(59, 130, 246, 0.05) !important;
    }

    /* Typography */
    h1, h2, h3 { color: #f8fafc !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='font-size: 2.5rem; margin-bottom: 0.5rem;'>Material Synchronization</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #94a3b8; font-size: 1.1rem; margin-bottom: 3rem;'>Ingest and manage your study foundation for AI augmented learning.</p>", unsafe_allow_html=True)

# Centralized Upload Card
with st.container():
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom:1.5rem;'>Ingest New Materials</h3>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Select high-quality PDF document", type=["pdf"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        if st.button("Initialize Synchronization", type="primary", use_container_width=True):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            try:
                with st.spinner("Processing document architecture..."):
                    # 1. Sync with Express Server
                    r = requests.post(f"{EXPRESS_URL}/api/pdf/upload", headers=headers, files=files, timeout=60)
                
                if r.status_code == 201:
                    pdf_id = r.json().get("pdf_id")
                    
                    # 2. Forward to FastAPI (Port 8000) for analysis and RAG embedding
                    with st.spinner("Analyzing and indexing in RAG vector database..."):
                        fastapi_headers = {"Authorization": f"Bearer {token}"}
                        fastapi_files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                        
                        try:
                            f_res = requests.post(
                                f"{FASTAPI_URL}/api/planner/analyze-pdf?pdf_id={pdf_id}",
                                headers=fastapi_headers,
                                files=fastapi_files,
                                timeout=120
                            )
                            if f_res.status_code != 200:
                                st.warning(f"Metadata synced, but indexing had issues: {f_res.text}")
                        except Exception as fe:
                            st.warning(f"Metadata synced, but could not reach indexing backend: {str(fe)}")
                    
                    st.success("Synchronization successful. Material is now accessible.")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error(f"Synchronization failed: {r.json().get('message', 'Protocol error')}")
            except Exception as e:
                st.error("Gateway connection timed out. Ensure your repository service is active.")
    st.markdown('</div>', unsafe_allow_html=True)

# Document Repository (Table)
st.markdown("<h3 style='margin-bottom:1.5rem;'>Synchronized Materials</h3>", unsafe_allow_html=True)

try:
    res = requests.get(f"{EXPRESS_URL}/api/student/pdfs", headers=headers, timeout=5)
    if res.status_code == 200:
        pdfs = res.json()
        if pdfs:
            import pandas as pd
            df = pd.DataFrame(pdfs)
            
            # Map columns safely to avoid KeyErrors
            if 'upload_date' in df.columns:
                df['uploaded_at'] = df['upload_date']
            
            if 'uploaded_at' in df.columns:
                df['uploaded_at'] = pd.to_datetime(df['uploaded_at']).dt.strftime('%Y-%m-%d %H:%M')
            else:
                df['uploaded_at'] = "Unknown"
                
            if 'size' in df.columns:
                df['size'] = df['size'].apply(lambda x: f"{x/1024/1024:.2f} MB" if pd.notnull(x) else "N/A")
            else:
                df['size'] = "N/A"
            
            st.dataframe(
                df[['filename', 'size', 'uploaded_at']], 
                use_container_width=True,
                column_config={
                    "filename": "Resource Name",
                    "size": "Data Volume",
                    "uploaded_at": "Sync Timestamp"
                },
                hide_index=True
            )
            
            # Action controls
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2 = st.columns([2, 1])
            with col2:
                selected_pdf = st.selectbox("Select material to manage", options=df['filename'].tolist(), label_visibility="collapsed")
                if st.button("Delete from Workspace", use_container_width=True):
                    # Find ID
                    doc_id = df[df['filename'] == selected_pdf]['id'].iloc[0]
                    requests.delete(f"{EXPRESS_URL}/api/pdf/{doc_id}", headers=headers)
                    st.success("Resource de-synchronized.")
                    time.sleep(1)
                    st.rerun()
        else:
            st.info("System awaiting initial material ingestion.")
    else:
        st.error("Repository service unreachable.")
except Exception as e:
    st.info("Awaiting synchronization with material database.")

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #475569; font-size: 0.75rem;'>EDUMIND AI • MATERIAL SYNC GATEWAY v2.0</div>", unsafe_allow_html=True)
