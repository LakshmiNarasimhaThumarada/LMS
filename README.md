# EduMind AI Study Planner

AI-powered study planner feature for the EduMind learning management system.

## Project Structure

- `backend/`: FastAPI application, LangGraph agents, and background workers.
- `frontend/`: Streamlit-based user interface.

## Quick Start

1. **Run Setup Script:**
   ```bash
   bash setup.sh
   ```

2. **Configure Environment:**
   Edit `backend/.env` and provide your API keys for GROQ, Google, SendGrid, etc.

3. **Start Backend:**
   ```bash
   cd backend
   uvicorn app:app --reload
   ```

4. **Start Worker:**
   ```bash
   cd backend
   celery -A workers.celery_app worker --loglevel=info
   ```

5. **Start Frontend:**
   ```bash
   streamlit run frontend/pages/study_planner.py
   ```

## Features

- **AI PDF Analysis:** Automatically extracts study topics from uploaded documents.
- **Dynamic Scheduling:** Generates personalized timetables using LangGraph.
- **Adaptive Rescheduling:** Adjusts your plan based on progress and missed sessions.
- **Multi-channel Notifications:** Email, SMS (Twilio), and Web Push alerts.
- **Calendar Sync:** Integration with Google Calendar and Outlook.
