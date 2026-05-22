from pywebpush import webpush, WebPushException
import json
from typing import Dict, Optional
from backend.config import settings

class NotificationService:
    """
    Multi-channel notification service.
    Sends study reminders via push, email, SMS.
    """
    
    def __init__(self):
        self.vapid_claims = {
            "sub": settings.VAPID_SUBJECT
        }
    
    def send_push_notification(
        self,
        subscription: Dict,
        message: Dict
    ) -> bool:
        """
        Send browser push notification.
        """
        
        try:
            # Add alarm sound and interaction parameters
            message['requireInteraction'] = True  # Stay until user interacts
            message['vibrate'] = [200, 100, 200, 100, 200]  # Strong vibration
            message['tag'] = 'study-alarm'  # Replace previous alarm
            
            response = webpush(
                subscription_info=subscription,
                data=json.dumps(message),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims=self.vapid_claims
            )
            
            return response.status_code == 201
            
        except WebPushException as e:
            print(f"Push notification failed: {e}")
            
            # If subscription is invalid, mark it for deletion
            if e.response and e.response.status_code in [404, 410]:
                # Subscription expired or invalid
                return False
            
            return False
        except Exception as e:
            print(f"Push error: {e}")
            return False
    
    def send_batch_notifications(
        self,
        user_id: str,
        message: Dict,
        channels: Dict[str, bool]
    ):
        """
        Send notification across multiple channels.
        """
        
        results = {}
        
        if channels.get('push'):
            # Logic to get user's push subscription from DB and send
            pass
        
        if channels.get('email'):
            from backend.services.email_service import EmailService
            email_service = EmailService()
            # Logic to send email
            pass
        
        if channels.get('sms'):
            from backend.services.sms_service import SMSService
            sms_service = SMSService()
            # Logic to send SMS
            pass
        
        return results
