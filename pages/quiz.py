import streamlit as st
import requests
import time
from design_system import *

# Page Config
st.set_page_config(
    page_title="EduMind | Assessment",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Global CSS
inject_custom_css()

# Custom Quiz CSS
st.markdown(f"""
<style>
    /* Configuration Card */
    .config-card {{
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 40px;
        max-width: 800px;
        margin: 0 auto;
    }}

    .config-label {{
        font-size: 16px;
        font-weight: 600;
        color: #f9fafb;
        margin-bottom: 12px;
        display: block;
    }}

    /* Dropdown Overrides */
    div[data-baseweb="select"] {{
        background-color: #111827 !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
    }}
    
    /* Slider Display */
    .difficulty-display {{
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 8px;
    }}
    .diff-easy {{ color: #10b981; }}
    .diff-medium {{ color: #f59e0b; }}
    .diff-hard {{ color: #ef4444; }}

    /* Counter Controls */
    .counter-row {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 24px;
        margin-bottom: 40px;
    }}
    .counter-btn button {{
        width: 44px !important;
        height: 44px !important;
        background-color: #374151 !important;
        border-radius: 8px !important;
        font-size: 20px !important;
        color: #f9fafb !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: none !important;
        box-shadow: none !important;
    }}
    .counter-btn button:hover {{
        background-color: #3b82f6 !important;
        transform: translateY(-2px);
    }}
    .count-display {{
        font-size: 24px;
        font-weight: bold;
        color: #f9fafb;
        width: 60px;
        text-align: center;
    }}

    /* Generate Button */
    .btn-generate button {{
        width: 100% !important;
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        padding: 18px !important;
        border-radius: 12px !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4) !important;
        transition: all 0.3s !important;
        border: none !important;
        color: white !important;
    }}
    .btn-generate button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 28px rgba(59, 130, 246, 0.6) !important;
    }}
</style>
""", unsafe_allow_html=True)

# Auth Check
if 'jwt_token' not in st.session_state:
    st.switch_page('pages/login.py')

# Ensure stable IPv4 connections for Windows
EXPRESS_BASE = "http://127.0.0.1:6000/api"
FASTAPI_BASE = "http://127.0.0.1:8000/api"
headers = {"Authorization": f"Bearer {st.session_state.jwt_token}"}

# --- Data Fetching ---
def fetch_materials():
    try:
        res = requests.get(f"{EXPRESS_BASE}/student/pdfs", headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        return []
    except Exception as e:
        print(f"[DEBUG QUIZ FETCH] Error: {e}")
        return []

# Initialize Session States for Counter & Quiz state
if 'q_count' not in st.session_state:
    st.session_state.q_count = 5

# --- Page Layout Logic ---
if 'active_quiz' not in st.session_state:
    # ==========================================
    # 1. QUIZ GENERATION CONFIGURATION VIEW
    # ==========================================
    
    st.markdown("""
    <div style="margin-bottom: 40px; text-align: center;">
        <div style="font-size: 32px; font-weight: bold; color: #f9fafb; margin-bottom: 8px;">Create Assessment</div>
        <div style="font-size: 16px; color: #9ca3af;">Generate a customized assessment based on your study materials.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="config-card">', unsafe_allow_html=True)

    # A. Select Material
    st.markdown('<label class="config-label">Select Study Material</label>', unsafe_allow_html=True)
    materials = fetch_materials()
    options = {m['filename']: m['id'] for m in materials}
    
    if not options:
        st.warning("No study materials found. Please upload a PDF in the 'My Materials' or 'Chat with AI' page first.")
        selected_filename = None
    else:
        selected_filename = st.selectbox("Choose a PDF...", options.keys(), label_visibility="collapsed", index=None)

    st.markdown('<br>', unsafe_allow_html=True)

    # B. Difficulty Slider
    st.markdown('<label class="config-label">Assessment Difficulty</label>', unsafe_allow_html=True)
    diff_map = {0: "Easy", 1: "Medium", 2: "Hard"}
    diff_val = st.select_slider("diff_slider", options=[0, 1, 2], value=1, label_visibility="collapsed")

    diff_label = diff_map[diff_val]
    diff_class = f"diff-{diff_label.lower()}"
    st.markdown(f'<div class="difficulty-display {diff_class}">{diff_label}</div>', unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)

    # C. Question Count
    st.markdown('<label class="config-label" style="text-align: center;">Question Count</label>', unsafe_allow_html=True)

    col_minus, col_val, col_plus = st.columns([1, 1, 1])

    with col_minus:
        st.markdown('<div class="counter-btn" style="display: flex; justify-content: flex-end;">', unsafe_allow_html=True)
        if st.button("-", key="minus_btn"):
            if st.session_state.q_count > 1:
                st.session_state.q_count -= 1
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_val:
        st.markdown(f'<div class="count-display" style="margin: 0 auto; padding-top: 10px;">{st.session_state.q_count}</div>', unsafe_allow_html=True)

    with col_plus:
        st.markdown('<div class="counter-btn">', unsafe_allow_html=True)
        if st.button("+", key="plus_btn"):
            if st.session_state.q_count < 20:
                st.session_state.q_count += 1
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)

    # D. Initialize Button
    st.markdown('<div class="btn-generate">', unsafe_allow_html=True)
    if st.button("Initialize Assessment", key="gen_btn"):
        if not selected_filename:
            st.error("Please select a study material first.")
        else:
            with st.spinner("Generating Questions..."):
                try:
                    payload = {
                        "pdf_id": options[selected_filename],
                        "difficulty": diff_label.lower(),
                        "num_questions": st.session_state.q_count
                    }
                    res = requests.post(f"{FASTAPI_BASE}/quiz/generate", json=payload, headers=headers, timeout=60)
                    
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.active_quiz = data
                        st.session_state.quiz_pdf_name = selected_filename
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_results = None
                        st.success("Assessment generated successfully!")
                        time.sleep(1.0)
                        st.rerun()
                    else:
                        st.error(f"Generation failed: {res.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # ==========================================
    # 2. QUIZ TAKING & SUBMISSION VIEW
    # ==========================================
    quiz = st.session_state.active_quiz
    quiz_id = quiz.get("quiz_id")
    questions = quiz.get("questions", [])
    
    st.markdown(f"""
    <div style="margin-bottom: 30px;">
        <div style="font-size: 28px; font-weight: bold; color: #f9fafb;">Assessment Session</div>
        <div style="font-size: 14px; color: #9ca3af;">Grounding Material: <b>{st.session_state.quiz_pdf_name}</b></div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.quiz_submitted:
        # Display Quiz taking form
        with st.form("quiz_form"):
            user_answers = {}
            
            for idx, q in enumerate(questions):
                st.markdown(f"### Question {idx+1}")
                st.markdown(f"**{q['question']}**")
                
                if q['type'] == 'mcq':
                    # Use radio buttons for MCQ
                    user_answers[idx] = st.radio(
                        f"q_input_{idx}",
                        options=q['options'],
                        key=f"ans_widget_{idx}",
                        label_visibility="collapsed",
                        index=None
                    )
                else:
                    # Use text area for Short Answer
                    user_answers[idx] = st.text_area(
                        f"q_input_{idx}",
                        key=f"ans_widget_{idx}",
                        label_visibility="collapsed",
                        placeholder="Write your explanation here..."
                    )
                st.markdown("<hr style='border-color: #374151; margin: 20px 0;'>", unsafe_allow_html=True)
                
            submitted = st.form_submit_button("Submit Assessment", type="primary")
            
            if submitted:
                # Validate that all questions are answered
                missing_answers = False
                answers_list = []
                for idx in range(len(questions)):
                    val = user_answers.get(idx)
                    if val is None or str(val).strip() == "":
                        missing_answers = True
                        break
                    answers_list.append(str(val))
                    
                if missing_answers:
                    st.error("Please answer all questions before submitting.")
                else:
                    with st.spinner("Grading assessment..."):
                        try:
                            # 1. Post answers to evaluation endpoint on FASTAPI
                            eval_payload = {
                                "quiz_id": quiz_id,
                                "answers": answers_list
                            }
                            res = requests.post(f"{FASTAPI_BASE}/quiz/evaluate", json=eval_payload, headers=headers, timeout=60)
                            
                            if res.status_code == 200:
                                eval_data = res.json()
                                st.session_state.quiz_results = eval_data
                                st.session_state.quiz_submitted = True
                                
                                # 2. Save final score in user progress via FASTAPI
                                save_payload = {
                                    "quiz_id": quiz_id,
                                    "score": eval_data["score"],
                                    "topic": st.session_state.quiz_pdf_name
                                }
                                requests.post(f"{FASTAPI_BASE}/quiz/save-result", json=save_payload, headers=headers, timeout=10)
                                
                                st.success("Assessment graded successfully!")
                                time.sleep(1.0)
                                st.rerun()
                            else:
                                st.error("Evaluation failed on grading server.")
                        except Exception as e:
                            st.error(f"Grading connection error: {e}")
                            
    else:
        # ==========================================
        # 3. QUIZ RESULTS & FEEDBACK VIEW
        # ==========================================
        results = st.session_state.quiz_results
        score = results.get("score", "0/0")
        percentage = results.get("percentage", 0)
        feedback_list = results.get("results", [])
        
        # Header score metrics
        col_metric, col_chart = st.columns([1, 2])
        with col_metric:
            st.metric("Total Score", score)
            
        with col_chart:
            # Render a custom progress bar for score percentage
            st.markdown(f"**Score Accuracy:** {round(percentage, 1)}%")
            st.progress(int(percentage) / 100)
            
        st.markdown("<br><hr style='border-color: #374151; margin: 20px 0;'>", unsafe_allow_html=True)
        st.markdown("### Question Feedback & Answers")
        
        for idx, f in enumerate(feedback_list):
            st.markdown(f"#### Question {idx+1}")
            st.markdown(f"**{f['question']}**")
            
            # Colored pass/fail badge
            if f['is_correct']:
                st.success("✅ Correct")
            else:
                st.error("❌ Incorrect")
                
            st.markdown(f"**Your Answer:** {f['user_answer']}")
            st.markdown(f"**Correct Key:** {f['correct_answer']}")
            st.info(f"**Feedback Explanation:** {f['explanation']}")
            st.markdown("<hr style='border-color: #1f2937; margin: 15px 0;'>", unsafe_allow_html=True)
            
        if st.button("Start New Assessment", type="primary", use_container_width=True):
            # Clear quiz session states and return to config card
            del st.session_state.active_quiz
            del st.session_state.quiz_pdf_name
            del st.session_state.quiz_submitted
            del st.session_state.quiz_results
            st.rerun()
