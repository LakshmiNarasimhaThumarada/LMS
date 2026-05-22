from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from backend.config import settings

class GoogleCalendarService:
    """Google Calendar integration with alarm support"""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, credentials_dict: Optional[Dict] = None):
        """
        Initialize with user credentials.
        """
        if credentials_dict:
            self.credentials = Credentials(**credentials_dict)
            # Handle token refresh if expired
            if self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            self.service = build('calendar', 'v3', credentials=self.credentials)
        else:
            self.credentials = None
            self.service = None
    
    @staticmethod
    def get_authorization_url(redirect_uri: str) -> str:
        """
        Get OAuth authorization URL.
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            scopes=GoogleCalendarService.SCOPES,
            redirect_uri=redirect_uri
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return authorization_url
    
    @staticmethod
    def exchange_code_for_credentials(code: str, redirect_uri: str) -> Dict:
        """
        Exchange authorization code for credentials.
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            scopes=GoogleCalendarService.SCOPES,
            redirect_uri=redirect_uri
        )
        
        flow.fetch_token(code=code)
        
        return {
            'token': flow.credentials.token,
            'refresh_token': flow.credentials.refresh_token,
            'token_uri': flow.credentials.token_uri,
            'client_id': flow.credentials.client_id,
            'client_secret': flow.credentials.client_secret,
            'scopes': flow.credentials.scopes
        }
    
    def add_study_session(
        self,
        session: Dict,
        timezone: str = 'Asia/Kolkata'
    ) -> str:
        """
        Add study session to Google Calendar with ALARM.
        """
        
        if not self.service:
            raise Exception("Calendar service not initialized")
        
        try:
            # Calculate start and end times
            start_datetime = datetime.strptime(
                f"{session['date']} {session['time']}",
                '%Y-%m-%d %H:%M'
            )
            end_datetime = start_datetime + timedelta(hours=session.get('duration', 1.5))
            
            # Build event
            event = {
                'summary': f"📚 Study: {session['chapter_name']}",
                'description': self._build_description(session),
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': timezone,
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 15},  # 15 min before (alarm)
                        {'method': 'popup', 'minutes': 5},   # 5 min before (alarm)
                        {'method': 'email', 'minutes': 60},  # 1 hour before (email)
                    ],
                },
                'colorId': '9',  # Blue color
                'guestsCanSeeOtherGuests': False,
                'visibility': 'private',
            }
            
            # Insert event
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return created_event['id']
            
        except HttpError as e:
            raise Exception(f"Google Calendar error: {str(e)}")
    
    def add_all_sessions(
        self,
        sessions: List[Dict],
        timezone: str = 'Asia/Kolkata'
    ) -> Dict[str, str]:
        """
        Add all study sessions to calendar.
        """
        
        event_ids = {}
        
        for session in sessions:
            try:
                event_id = self.add_study_session(session, timezone)
                event_ids[session['id']] = event_id
            except Exception as e:
                print(f"Failed to add session {session['id']}: {e}")
        
        return event_ids
    
    def delete_session(self, event_id: str):
        """Delete event from calendar"""
        
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
        except HttpError as e:
            print(f"Failed to delete event: {e}")
    
    def _build_description(self, session: Dict) -> str:
        """Build event description"""
        
        description = f"Study session for {session['chapter_name']}\n\n"
        
        if session.get('topics'):
            description += "Topics to cover:\n"
            for topic in session['topics']:
                description += f"• {topic}\n"
        
        description += f"\nDuration: {session.get('duration', 1.5)} hours\n"
        description += f"Type: {session.get('type', 'study').replace('_', ' ').title()}\n"
        description += "\n📱 Open EduMind to start studying"
        
        return description
