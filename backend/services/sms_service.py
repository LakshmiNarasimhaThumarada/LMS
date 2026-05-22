from twilio.rest import Client
from typing import Dict
from backend.config import settings

class SMSService:
    """Twilio SMS service"""
    
    def __init__(self):
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.from_number = settings.TWILIO_PHONE_NUMBER
        else:
            self.client = None
    
    def send_study_reminder(
        self,
        phone: str,
        session: Dict
    ) -> bool:
        """
        Send SMS study reminder.
        """
        
        if not self.client:
            print("Twilio not configured")
            return False
        
        try:
            # Keep SMS short (160 chars)
            message_body = (
                f"📚 EduMind: {session['chapter_name']} "
                f"starts at {session['time']}! "
                f"Duration: {session['duration']}h. Good luck!"
            )
            
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=phone
            )
            
            return message.sid is not None
            
        except Exception as e:
            print(f"SMS failed: {e}")
            return False
    
    def send_missed_session_reminder(
        self,
        phone: str,
        session: Dict
    ) -> bool:
        """Send reminder for missed session"""
        
        if not self.client:
            return False
        
        try:
            message_body = (
                f"📚 You missed: {session['chapter_name']}. "
                f"Would you like to reschedule? Reply YES or visit EduMind."
            )
            
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=phone
            )
            
            return message.sid is not None
            
        except Exception as e:
            print(f"SMS failed: {e}")
            return False
