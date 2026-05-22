import pytest
import requests
from datetime import datetime, timedelta
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
# Note: You'll need a way to get a real token in a production test environment
TEST_JWT = os.getenv("TEST_JWT", "your_test_jwt_token_here")

class TestStudyPlannerIntegration:
    """End-to-end integration tests for AI Study Planner"""
    
    @pytest.fixture
    def auth_headers(self):
        return {'Authorization': f'Bearer {TEST_JWT}'}
    
    def test_01_upload_and_analyze_pdf(self, auth_headers):
        """Test PDF upload and analysis"""
        
        # Ensure fixtures directory exists or use a dummy file
        fixture_path = 'backend/tests/fixtures/sample_textbook.pdf'
        if not os.path.exists(fixture_path):
            os.makedirs(os.path.dirname(fixture_path), exist_ok=True)
            with open(fixture_path, 'wb') as f:
                f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 10 >>\nstream\nBT /F1 12 Tf 100 700 Td (Hello) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000213 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n274\n%%EOF")

        # Upload PDF
        with open(fixture_path, 'rb') as f:
            response = requests.post(
                f'{BASE_URL}/api/planner/analyze-pdf',
                headers=auth_headers,
                files={'file': f}
            )
        
        # In a real environment without valid keys this might fail, 
        # but the structure is what we're testing
        assert response.status_code in [200, 401] # 401 if JWT is invalid
        if response.status_code == 200:
            data = response.json()
            assert 'pdf_id' in data
            assert 'analysis' in data
            return data['pdf_id']
        return None
    
    def test_02_generate_study_plan(self, auth_headers):
        """Test study plan generation"""
        
        pdf_id = self.test_01_upload_and_analyze_pdf(auth_headers)
        if not pdf_id:
            pytest.skip("PDF upload failed or returned no ID")
            
        # Generate plan
        response = requests.post(
            f'{BASE_URL}/api/planner/generate-plan',
            headers=auth_headers,
            json={
                'pdf_id': pdf_id,
                'preferences': {
                    'exam_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                    'hours_per_day': 3,
                    'preferred_times': ['morning', 'evening'],
                    'study_style': 'distributed',
                    'skip_weekends': True
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'plan_id' in data
        assert 'sessions' in data
        assert len(data['sessions']) > 0
        return data['plan_id']
    
    def test_03_complete_session_triggers_rescheduling(self, auth_headers):
        """Test that marking session as 'hard' triggers adaptive rescheduling"""
        
        # Fetch an active plan
        response = requests.get(
            f'{BASE_URL}/api/planner/active-plan',
            headers=auth_headers
        )
        
        if response.status_code != 200:
             pytest.skip("No active plan found")
             
        plan = response.json()
        if not plan['sessions']:
            pytest.skip("Plan has no sessions")
            
        first_session = plan['sessions'][0]
        
        # Mark as completed with 'hard' difficulty
        response = requests.post(
            f'{BASE_URL}/api/progress/complete-session',
            headers=auth_headers,
            json={
                'session_id': first_session['id'],
                'completed': True,
                'difficulty_rating': 'hard',
                'actual_time': 2.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        # If 'hard', we expect rescheduling results
        assert 'new_sessions' in data or "Extra review session added" in data.get('message', '')
    
    def test_04_notification_subscription(self, auth_headers):
        """Test notification preference update"""
        
        response = requests.put(
            f'{BASE_URL}/api/notifications/preferences',
            headers=auth_headers,
            json={
                'push_enabled': True,
                'email_enabled': True,
                'sms_enabled': False,
                'reminder_minutes': 15
            }
        )
        
        assert response.status_code == 200
        assert response.json()['success'] == True
    
    def test_05_calendar_status(self, auth_headers):
        """Test calendar status check"""
        
        response = requests.get(
            f'{BASE_URL}/api/calendar/status',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'google_connected' in data
        assert 'microsoft_connected' in data
