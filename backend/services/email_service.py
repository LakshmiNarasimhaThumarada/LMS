from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import Dict
from backend.config import settings

class EmailService:
    """SendGrid email service"""
    
    def __init__(self):
        self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
        self.from_email = settings.FROM_EMAIL
    
    def send_study_reminder(
        self,
        email: str,
        session: Dict
    ) -> bool:
        """
        Send email study reminder.
        """
        
        try:
            # Build email content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background: #f4f6f9; padding: 20px; }}
                    .container {{ background: white; padding: 30px; border-radius: 12px; max-width: 600px; margin: 0 auto; }}
                    .header {{ background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                    .content {{ padding: 20px 0; }}
                    .session {{ background: #f0f4ff; padding: 15px; border-radius: 8px; margin: 15px 0; }}
                    .cta {{ background: #3b82f6; color: white; padding: 14px 32px; text-decoration: none; border-radius: 8px; display: inline-block; margin-top: 20px; }}
                    .footer {{ text-align: center; color: #6b7280; font-size: 14px; margin-top: 30px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📚 Study Time Reminder</h1>
                    </div>
                    
                    <div class="content">
                        <p>Hello!</p>
                        <p>Your scheduled study session is starting soon:</p>
                        
                        <div class="session">
                            <h3>{session['chapter_name']}</h3>
                            <p><strong>📅 Date:</strong> {session['date']}</p>
                            <p><strong>⏰ Time:</strong> {session['time']}</p>
                            <p><strong>⏱️ Duration:</strong> {session['duration']} hours</p>
                            {f"<p><strong>📖 Topics:</strong> {', '.join(session.get('topics', []))}</p>" if session.get('topics') else ""}
                        </div>
                        
                        <p>Get ready to study! Make sure you have:</p>
                        <ul>
                            <li>Your study materials ready</li>
                            <li>A quiet, distraction-free environment</li>
                            <li>Water and snacks nearby</li>
                            <li>Timer or clock visible</li>
                        </ul>
                        
                        <center>
                            <a href="https://edumind.com/study?session={session['id']}" class="cta">
                                Start Studying Now
                            </a>
                        </center>
                    </div>
                    
                    <div class="footer">
                        <p>EduMind - Your AI Study Partner</p>
                        <p><a href="https://edumind.com/settings">Manage notification preferences</a></p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=self.from_email,
                to_emails=email,
                subject=f"📚 Study Reminder: {session['chapter_name']}",
                html_content=html_content
            )
            
            response = self.client.send(message)
            return response.status_code == 202
            
        except Exception as e:
            print(f"Email failed: {e}")
            return False
    
    def send_daily_summary(
        self,
        email: str,
        summary: Dict
    ) -> bool:
        """Send daily progress summary"""
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body>
            <h2>📊 Your Daily Study Summary</h2>
            <p>Sessions completed today: {summary['completed_today']}</p>
            <p>Total study time: {summary['hours_today']} hours</p>
            <p>Current streak: {summary['streak']} days 🔥</p>
            
            <h3>Tomorrow's Schedule:</h3>
            <ul>
                {''.join(f"<li>{s['time']} - {s['chapter_name']}</li>" for s in summary['tomorrow_sessions'])}
            </ul>
            
            <p>Keep up the great work! 💪</p>
        </body>
        </html>
        """
        
        message = Mail(
            from_email=self.from_email,
            to_emails=email,
            subject="📊 Your Daily Study Summary",
            html_content=html_content
        )
        
        try:
            response = self.client.send(message)
            return response.status_code == 202
        except Exception as e:
            print(f"Daily summary email failed: {e}")
            return False
