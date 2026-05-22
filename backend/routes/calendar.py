from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId

from backend.services.calendar_service import GoogleCalendarService
from backend.services.microsoft_calendar_service import MicrosoftCalendarService
from backend.utils.auth import require_jwt

router = APIRouter()

# Dependency to get database
async def get_db(request: Request):
    return request.app.state.db

# Dependency to get current user
async def get_user(user_data: dict = Depends(require_jwt)):
    return user_data

@router.get("/google/authorize")
async def authorize_google_calendar(
    user = Depends(get_user)
):
    """
    Step 1: Get Google Calendar authorization URL.
    """
    # Use a generic or user-specific redirect URI if needed
    redirect_uri = "http://localhost:8000/api/calendar/google/callback"
    auth_url = GoogleCalendarService.get_authorization_url(redirect_uri)
    
    return {"authorization_url": auth_url}

@router.get("/google/callback")
async def google_calendar_callback(
    code: str,
    db = Depends(get_db),
    # We might need to handle the state/user mapping differently in a real flow
    # For now assuming user is in session or passed in some way
    user = Depends(get_user) 
):
    """
    Step 2: OAuth callback - exchange code for credentials.
    """
    
    try:
        redirect_uri = "http://localhost:8000/api/calendar/google/callback"
        
        # Exchange code for credentials
        credentials = GoogleCalendarService.exchange_code_for_credentials(code, redirect_uri)
        
        # Store credentials in database
        await db.calendar_credentials.update_one(
            {'user_id': user['id'], 'provider': 'google'},
            {
                '$set': {
                    'user_id': user['id'],
                    'provider': 'google',
                    'credentials': credentials,
                    'created_at': datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return {"success": True, "message": "Google Calendar connected"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync-plan/{plan_id}")
async def sync_plan_to_calendar(
    plan_id: str,
    provider: str = 'google',  # or 'microsoft'
    db = Depends(get_db),
    user = Depends(get_user)
):
    """
    Sync entire study plan to calendar.
    """
    
    try:
        # Get study plan
        plan = await db.study_plans.find_one({
            '_id': plan_id,
            'user_id': user['id']
        })
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Get calendar credentials
        calendar_creds = await db.calendar_credentials.find_one({
            'user_id': user['id'],
            'provider': provider
        })
        
        if not calendar_creds:
            raise HTTPException(
                status_code=400,
                detail=f"{provider} calendar not connected. Authorize first."
            )
        
        # Sync based on provider
        if provider == 'google':
            service = GoogleCalendarService(calendar_creds['credentials'])
            event_ids = service.add_all_sessions(plan['sessions'])
        elif provider == 'microsoft':
            service = MicrosoftCalendarService(calendar_creds['credentials'].get('access_token'))
            event_ids = {}
            for session in plan['sessions']:
                event_id = service.add_study_session(session)
                event_ids[session['id']] = event_id
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        # Store event IDs in plan
        await db.study_plans.update_one(
            {'_id': plan_id},
            {
                '$set': {
                    f'calendar_sync.{provider}': {
                        'synced_at': datetime.utcnow(),
                        'event_ids': event_ids
                    }
                }
            }
        )
        
        return {
            "success": True,
            "provider": provider,
            "events_created": len(event_ids)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_calendar_status(
    db = Depends(get_db),
    user = Depends(get_user)
):
    """Check which calendars are connected"""
    
    google_creds = await db.calendar_credentials.find_one({
        'user_id': user['id'],
        'provider': 'google'
    })
    
    microsoft_creds = await db.calendar_credentials.find_one({
        'user_id': user['id'],
        'provider': 'microsoft'
    })
    
    return {
        'google_connected': google_creds is not None,
        'microsoft_connected': microsoft_creds is not None
    }
