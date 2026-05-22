from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Optional, List
import os
from datetime import datetime, timedelta
from bson import ObjectId
import shutil

from backend.agents.content_analyzer import ContentAnalyzerAgent
from backend.agents.schedule_generator import ScheduleGeneratorAgent
from backend.models.planner_models import (
    PDFAnalysisResponse, PDFAnalysisResult, GeneratePlanRequest, 
    GeneratePlanResponse, StudyPlan, Session
)
from backend.utils.auth import require_jwt, verify_jwt

router = APIRouter()

# Dependency to get database
async def get_db(request: Request):
    return request.app.state.db

# Dependency to get current user
async def get_user(user_data: dict = Depends(require_jwt)):
    return user_data

@router.post("/analyze-pdf", response_model=PDFAnalysisResponse)
async def analyze_pdf(
    file: UploadFile = File(...),
    db = Depends(get_db),
    user = Depends(get_user)
):
    """
    Analyzes uploaded PDF for study planning.
    """
    # Use relative paths for Windows compatibility
    temp_dir = "./temp"
    data_dir = "./data/pdfs"
    os.makedirs(temp_dir, exist_ok=True)
    
    temp_file_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save temp file
        file_size = 0
        with open(temp_file_path, "wb") as f:
            while chunk := await file.read(1024 * 1024):  # Read in 1MB chunks
                file_size += len(chunk)
                if file_size > 50 * 1024 * 1024:  # 50MB limit
                    f.close()
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                    raise HTTPException(status_code=400, detail="File too large (max 50MB)")
                f.write(chunk)
        
        # Run Content Analyzer Agent
        analyzer = ContentAnalyzerAgent()
        analysis_dict = analyzer.analyze(temp_file_path)
        
        # Generate PDF ID
        pdf_id = str(ObjectId())
        
        # Save to permanent storage
        user_pdf_dir = os.path.join(data_dir, str(user['id']))
        os.makedirs(user_pdf_dir, exist_ok=True)
        permanent_path = os.path.join(user_pdf_dir, f"{pdf_id}.pdf")
        
        # Move file (using shutil for cross-drive support)
        shutil.copy2(temp_file_path, permanent_path)
        os.remove(temp_file_path)
        
        # Store in MongoDB
        pdf_doc = {
            '_id': pdf_id,
            'user_id': user['id'],
            'filename': file.filename,
            'file_path': permanent_path,
            'file_size': file_size,
            'analysis': analysis_dict,
            'created_at': datetime.utcnow(),
            'status': 'analyzed'
        }
        
        await db.pdf_analysis.insert_one(pdf_doc)
        
        return PDFAnalysisResponse(
            pdf_id=pdf_id,
            filename=file.filename,
            analysis=PDFAnalysisResult(**analysis_dict),
            created_at=pdf_doc['created_at']
        )
        
    except HTTPException:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/pdf-analysis/{pdf_id}", response_model=PDFAnalysisResponse)
async def get_pdf_analysis(
    pdf_id: str,
    db = Depends(get_db),
    user = Depends(get_user)
):
    try:
        analysis_doc = await db.pdf_analysis.find_one({
            '_id': pdf_id,
            'user_id': user['id']
        })
        
        if not analysis_doc:
            raise HTTPException(status_code=404, detail="PDF analysis not found")
        
        return PDFAnalysisResponse(
            pdf_id=analysis_doc['_id'],
            filename=analysis_doc['filename'],
            analysis=PDFAnalysisResult(**analysis_doc['analysis']),
            created_at=analysis_doc['created_at']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-pdfs")
async def get_user_pdfs(
    db = Depends(get_db),
    user = Depends(get_user)
):
    try:
        pdfs = await db.pdf_analysis.find(
            {'user_id': user['id']},
            {
                '_id': 1,
                'filename': 1,
                'created_at': 1,
                'analysis.total_topics': 1,
                'analysis.difficulty': 1,
                'analysis.estimated_hours.total': 1
            }
        ).sort('created_at', -1).to_list(length=100)
        
        return [
            {
                'pdf_id': pdf['_id'],
                'filename': pdf['filename'],
                'created_at': pdf['created_at'],
                'total_topics': pdf['analysis']['total_topics'],
                'difficulty': pdf['analysis']['difficulty'],
                'estimated_hours': pdf['analysis']['estimated_hours']['total']
            }
            for pdf in pdfs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-plan", response_model=GeneratePlanResponse)
async def generate_study_plan(
    request: GeneratePlanRequest,
    db = Depends(get_db),
    user = Depends(get_user)
):
    """
    Generates personalized study timetable.
    """
    try:
        # Get PDF analysis
        pdf_analysis = await db.pdf_analysis.find_one({
            '_id': request.pdf_id,
            'user_id': user['id']
        })
        
        if not pdf_analysis:
            raise HTTPException(status_code=404, detail="PDF not found")
        
        # Generate schedule using LangGraph agent
        generator = ScheduleGeneratorAgent()
        schedule = generator.generate(
            analysis=pdf_analysis['analysis'],
            preferences=request.preferences.dict()
        )
        
        # Generate plan ID
        plan_id = str(ObjectId())
        
        # Store in MongoDB
        plan_doc = {
            '_id': plan_id,
            'user_id': user['id'],
            'pdf_id': request.pdf_id,
            'pdf_filename': pdf_analysis['filename'],
            'sessions': schedule['sessions'],
            'summary': schedule['summary'],
            'preferences': request.preferences.dict(),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'status': 'active'
        }
        
        await db.study_plans.insert_one(plan_doc)
        
        # Schedule notifications for all sessions
        from backend.workers.notification_worker import schedule_study_reminder
        
        # Get user notification preferences
        notif_prefs = await db.notification_preferences.find_one({'user_id': user['id']})
        
        if notif_prefs:
            for session in schedule['sessions']:
                schedule_study_reminder.delay(
                    user_id=user['id'],
                    session=session,
                    notification_prefs=notif_prefs
                )
        
        return GeneratePlanResponse(
            plan_id=plan_id,
            sessions=schedule['sessions'],
            summary=schedule['summary'],
            created_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {str(e)}")

@router.get("/study-plan/{plan_id}", response_model=StudyPlan)
async def get_study_plan(
    plan_id: str,
    db = Depends(get_db),
    user = Depends(get_user)
):
    try:
        plan = await db.study_plans.find_one({
            '_id': plan_id,
            'user_id': user['id']
        })
        
        if not plan:
            raise HTTPException(status_code=404, detail="Study plan not found")
        
        # Map _id to plan_id for Pydantic
        plan['plan_id'] = plan.pop('_id')
        return StudyPlan(**plan)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active-plan", response_model=Optional[StudyPlan])
async def get_active_plan(
    db = Depends(get_db),
    user = Depends(get_user)
):
    try:
        plan = await db.study_plans.find_one({
            'user_id': user['id'],
            'status': 'active'
        }, sort=[('created_at', -1)])
        
        if not plan:
            return None
        
        plan['plan_id'] = plan.pop('_id')
        return StudyPlan(**plan)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/upcoming-sessions", response_model=List[Session])
async def get_upcoming_sessions(
    days: int = 7,
    db = Depends(get_db),
    user = Depends(get_user)
):
    try:
        plan = await db.study_plans.find_one({
            'user_id': user['id'],
            'status': 'active'
        })
        
        if not plan:
            return []
        
        # Filter sessions for next N days
        today_date = datetime.now()
        today_str = today_date.strftime('%Y-%m-%d')
        end_date_str = (today_date + timedelta(days=days)).strftime('%Y-%m-%d')
        
        upcoming = [
            s for s in plan['sessions']
            if today_str <= s['date'] <= end_date_str
        ]
        
        return sorted(upcoming, key=lambda x: (x['date'], x['time']))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/plan/{plan_id}/pause")
async def pause_plan(
    plan_id: str,
    db = Depends(get_db),
    user = Depends(get_user)
):
    try:
        result = await db.study_plans.update_one(
            {'_id': plan_id, 'user_id': user['id']},
            {'$set': {'status': 'paused', 'updated_at': datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        return {"success": True, "status": "paused"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/plan/{plan_id}/resume")
async def resume_plan(
    plan_id: str,
    db = Depends(get_db),
    user = Depends(get_user)
):
    try:
        result = await db.study_plans.update_one(
            {'_id': plan_id, 'user_id': user['id']},
            {'$set': {'status': 'active', 'updated_at': datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        return {"success": True, "status": "active"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
