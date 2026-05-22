import requests
from typing import Dict, List
from datetime import datetime, timedelta

class MicrosoftCalendarService:
    """Microsoft Outlook/Office 365 Calendar integration"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        self.base_url = 'https://graph.microsoft.com/v1.0/me'
    
    def add_study_session(
        self,
        session: Dict,
        timezone: str = 'Asia/Kolkata'
    ) -> str:
        """
        Add study session to Outlook Calendar with ALARM.
        """
        
        try:
            # Calculate times
            start_datetime = datetime.strptime(
                f"{session['date']} {session['time']}",
                '%Y-%m-%d %H:%M'
            )
            end_datetime = start_datetime + timedelta(hours=session.get('duration', 1.5))
            
            # Build event (Microsoft Graph format)
            event = {
                'subject': f"📚 Study: {session['chapter_name']}",
                'body': {
                    'contentType': 'Text',
                    'content': self._build_description(session)
                },
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': timezone
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': timezone
                },
                'isReminderOn': True,
                'reminderMinutesBeforeStart': 15,  # 15 min alarm
                'categories': ['EduMind', 'Study'],
                'sensitivity': 'private'
            }
            
            # Create event
            response = requests.post(
                f'{self.base_url}/events',
                headers=self.headers,
                json=event
            )
            
            response.raise_for_status()
            return response.json()['id']
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Microsoft Calendar error: {str(e)}")
    
    def _build_description(self, session: Dict) -> str:
        """Build description using static logic from Google service if needed or reimplement"""
        description = f"Study session for {session['chapter_name']}\n\n"
        if session.get('topics'):
            description += "Topics to cover:\n"
            for topic in session['topics']:
                description += f"• {topic}\n"
        description += f"\nDuration: {session.get('duration', 1.5)} hours\n"
        description += f"Type: {session.get('type', 'study').replace('_', ' ').title()}\n"
        description += "\n📱 Open EduMind to start studying"
        return description
