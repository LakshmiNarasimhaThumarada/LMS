from celery import shared_task
from datetime import datetime, timedelta
import redis
import json

from backend.services.notification_service import NotificationService
from backend.services.email_service import EmailService
from backend.services.sms_service import SMSService
from backend.workers.celery_app import celery_app
from backend.config import settings

# Redis client
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

@shared_task(name='backend.workers.notification_worker.process_scheduled_notifications')
def process_scheduled_notifications():
    """
    Checks Redis for notifications due now and sends them.
    Runs every minute via Celery Beat.
    """
    try:
        now = datetime.utcnow().timestamp()
        
        # Get notifications due now (score <= current timestamp)
        notifications = redis_client.zrangebyscore(
            'scheduled_notifications',
            min=0,
            max=now,
            withscores=True
        )
        
        if not notifications:
            return {"processed": 0}
        
        notification_service = NotificationService()
        processed = 0
        
        for notif_json, score in notifications:
            try:
                notif = json.loads(notif_json)
                
                # Send notification based on channels enabled
                if notif.get('push_enabled'):
                    notification_service.send_push_notification(
                        subscription=notif['push_subscription'],
                        message=notif['message']
                    )
                
                if notif.get('email_enabled'):
                    email_service = EmailService()
                    email_service.send_study_reminder(
                        email=notif['email'],
                        session=notif['session']
                    )
                
                if notif.get('sms_enabled'):
                    sms_service = SMSService()
                    sms_service.send_study_reminder(
                        phone=notif['phone'],
                        session=notif['session']
                    )
                
                # Remove from queue
                redis_client.zrem('scheduled_notifications', notif_json)
                processed += 1
                
            except Exception as e:
                print(f"Error processing notification: {e}")
                # Keep in queue for retry
        
        return {"processed": processed}
        
    except Exception as e:
        print(f"Error in process_scheduled_notifications: {e}")
        return {"error": str(e)}

@shared_task(name='backend.workers.notification_worker.schedule_study_reminder')
def schedule_study_reminder(user_id: str, session: dict, notification_prefs: dict):
    """
    Schedules a study reminder in Redis for future delivery.
    Called when a study plan is created or updated.
    """
    try:
        # Calculate reminder time (15 minutes before session)
        session_time = datetime.fromisoformat(
            f"{session['date']}T{session['time']}:00"
        )
        reminder_time = session_time - timedelta(minutes=15)
        
        # Build notification object
        notification = {
            'user_id': user_id,
            'session_id': session['id'],
            'session': session,
            'message': {
                'title': '🔔 Study Reminder',
                'body': f"{session['chapter']} starts in 15 minutes!",
                'icon': '/static/icon.png',
                'badge': '/static/badge.png',
                'data': {
                    'session_id': session['id'],
                    'url': f'/study?session={session["id"]}'
                }
            },
            
            # Notification channels (from user preferences)
            'push_enabled': notification_prefs.get('push_enabled', False),
            'push_subscription': notification_prefs.get('push_subscription'),
            
            'email_enabled': notification_prefs.get('email_enabled', False),
            'email': notification_prefs.get('email'),
            
            'sms_enabled': notification_prefs.get('sms_enabled', False),
            'phone': notification_prefs.get('phone'),
        }
        
        # Add to Redis sorted set (score = timestamp)
        redis_client.zadd(
            'scheduled_notifications',
            {json.dumps(notification): reminder_time.timestamp()}
        )
        
        return {"scheduled": True, "reminder_time": reminder_time.isoformat()}
        
    except Exception as e:
        print(f"Error scheduling reminder: {e}")
        return {"error": str(e)}

@shared_task(name='backend.workers.notification_worker.check_missed_sessions')
def check_missed_sessions():
    """
    Checks for missed study sessions and sends reminders.
    Runs every hour via Celery Beat.
    """
    # Implementation: Query MongoDB for sessions where:
    # - date + time < now
    # - completed = false
    # - missed_reminder_sent = false
    # Send "You missed your session, would you like to reschedule?" notification
    pass

@shared_task(name='backend.workers.notification_worker.send_daily_summary')
def send_daily_summary():
    """
    Sends daily progress summary to active users.
    Runs once daily at 8 PM via Celery Beat.
    """
    # Implementation: Query active users
    # Calculate: sessions completed today, streak, upcoming sessions tomorrow
    # Send email summary
    pass
