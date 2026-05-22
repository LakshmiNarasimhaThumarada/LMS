from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List

from backend.agents.reschedule_agent import RescheduleAgent
from backend.utils.auth import require_jwt

router = APIRouter()

# Dependency to get database
async def get_db(request: Request):
    return request.app.state.db

# Dependency to get current user
async def get_user(user_data: dict = Depends(require_jwt)):
    return user_data

class CompleteSessionRequest(BaseModel):
    session_id: str
    completed: bool = True
    difficulty_rating: Optional[str] = None  # 'easy', 'medium', 'hard'
    actual_time: Optional[float] = None  # Actual hours spent
    notes: Optional[str] = None

def calculate_streak(completed_sessions: list) -> int:
    """Calculate consecutive days streak"""
    
    if not completed_sessions:
        return 0
    
    # Get unique dates from completed_at, sorted descending
    dates = sorted(
        set(s['completed_at'].date() for s in completed_sessions if s.get('completed_at')),
        reverse=True
    )
    
    if not dates:
        return 0
    
    # Check if today has activity or if yesterday had activity (to maintain streak)
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    if dates[0] != today and dates[0] != yesterday:
        # Streak broken
        return 0
    
    # Count consecutive days
    streak = 1
    for i in range(len(dates) - 1):
        if (dates[i] - dates[i+1]).days == 1:
            streak += 1
        else:
            break
    
    return streak

@router.post("/complete-session")
async def complete_session(
    request: CompleteSessionRequest,
    db = Depends(get_db),
    user = Depends(get_user)
):
    """
    Mark session as complete and trigger adaptive rescheduling if needed.
    """
    
    try:
        # Find plan containing this session
        plan = await db.study_plans.find_one({
            'user_id': user['id'],
            'status': 'active',
            'sessions.id': request.session_id
        })
        
        if not plan:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update session
        session_index = next(
            i for i, s in enumerate(plan['sessions'])
            if s['id'] == request.session_id
        )
        
        now = datetime.utcnow()
        update_data = {
            f'sessions.{session_index}.completed': request.completed,
            f'sessions.{session_index}.completed_at': now,
            'updated_at': now
        }
        
        if request.difficulty_rating:
            update_data[f'sessions.{session_index}.difficulty_rating'] = request.difficulty_rating
        
        if request.actual_time:
            update_data[f'sessions.{session_index}.actual_time'] = request.actual_time
        
        if request.notes:
            update_data[f'sessions.{session_index}.notes'] = request.notes
        
        await db.study_plans.update_one(
            {'_id': plan['_id']},
            {'$set': update_data}
        )
        
        # If marked as 'hard', trigger adaptive rescheduling
        if request.difficulty_rating == 'hard':
            reschedule_agent = RescheduleAgent()
            
            result = reschedule_agent.reschedule(
                plan_id=plan['_id'],
                user_id=user['id'],
                trigger_type='difficulty',
                affected_session=plan['sessions'][session_index],
                current_sessions=plan['sessions']
            )
            
            # Add new review sessions to plan
            if result['new_sessions']:
                await db.study_plans.update_one(
                    {'_id': plan['_id']},
                    {
                        '$push': {
                            'sessions': {'$each': result['new_sessions']}
                        }
                    }
                )
                
                return {
                    "success": True,
                    "message": "Session completed. Extra review session added.",
                    "new_sessions": result['new_sessions']
                }
        
        return {"success": True, "message": "Session completed"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_progress_stats(
    db = Depends(get_db),
    user = Depends(get_user)
):
    """
    Get user's overall progress statistics.
    """
    
    try:
        plan = await db.study_plans.find_one({
            'user_id': user['id'],
            'status': 'active'
        })
        
        if not plan:
            return {
                "total_sessions": 0,
                "completed_sessions": 0,
                "completion_rate": 0,
                "total_hours_studied": 0,
                "current_streak": 0,
                "weak_topics": [],
                "upcoming_today": []
            }
        
        # Calculate stats
        total = len(plan['sessions'])
        completed = [s for s in plan['sessions'] if s.get('completed')]
        
        completion_rate = (len(completed) / total * 100) if total > 0 else 0
        
        total_hours = sum(
            s.get('actual_time', s.get('duration', 0))
            for s in completed
        )
        
        # Calculate streak
        streak = calculate_streak(completed)
        
        # Find weak topics (marked as 'hard')
        weak_sessions = [
            s for s in completed
            if s.get('difficulty_rating') == 'hard'
        ]
        
        weak_topics = list(set(
            s['chapter_name'] for s in weak_sessions
        ))
        
        # Today's upcoming sessions
        today_str = datetime.now().strftime('%Y-%m-%d')
        upcoming_today = [
            s for s in plan['sessions']
            if s['date'] == today_str and not s.get('completed')
        ]
        
        return {
            "total_sessions": total,
            "completed_sessions": len(completed),
            "completion_rate": round(completion_rate, 1),
            "total_hours_studied": round(total_hours, 1),
            "current_streak": streak,
            "weak_topics": weak_topics,
            "upcoming_today": upcoming_today
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
