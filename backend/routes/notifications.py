from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

from backend.utils.auth import require_jwt

router = APIRouter()

# Dependency to get database
async def get_db(request: Request):
    return request.app.state.db

# Dependency to get current user
async def get_user(user_data: dict = Depends(require_jwt)):
    return user_data

class PushSubscription(BaseModel):
    endpoint: str
    keys: Dict[str, str]  # p256dh, auth

class NotificationPreferences(BaseModel):
    push_enabled: bool = False
    push_subscription: Optional[PushSubscription] = None
    email_enabled: bool = True
    email_address: Optional[str] = None
    sms_enabled: bool = False
    phone_number: Optional[str] = None
    reminder_minutes: int = 15  # Minutes before session

@router.post("/subscribe-push")
async def subscribe_push_notifications(
    subscription: PushSubscription,
    db = Depends(get_db),
    user = Depends(get_user)
):
    """
    Subscribe to browser push notifications.
    """
    
    try:
        # Update user's notification preferences
        await db.notification_preferences.update_one(
            {'user_id': user['id']},
            {
                '$set': {
                    'push_enabled': True,
                    'push_subscription': subscription.dict(),
                    'updated_at': datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return {"success": True, "message": "Push notifications enabled"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/preferences")
async def update_notification_preferences(
    preferences: NotificationPreferences,
    db = Depends(get_db),
    user = Depends(get_user)
):
    """Update all notification preferences"""
    
    try:
        await db.notification_preferences.update_one(
            {'user_id': user['id']},
            {
                '$set': {
                    **preferences.dict(),
                    'user_id': user['id'],
                    'updated_at': datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return {"success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preferences", response_model=NotificationPreferences)
async def get_notification_preferences(
    db = Depends(get_db),
    user = Depends(get_user)
):
    """Get current notification preferences"""
    
    try:
        prefs = await db.notification_preferences.find_one({'user_id': user['id']})
        
        if not prefs:
            # Return defaults
            return NotificationPreferences()
        
        return NotificationPreferences(**prefs)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
