import redis
import json
from typing import List, Dict, Optional
from datetime import datetime
from backend.config import settings

class RedisCache:
    def __init__(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    def schedule_notification(self, notification: Dict, send_at: datetime):
        """Add notification to scheduled queue"""
        self.client.zadd(
            'scheduled_notifications',
            {json.dumps(notification): send_at.timestamp()}
        )
    
    def get_due_notifications(self) -> List[Dict]:
        """Get notifications that are due now"""
        now = datetime.utcnow().timestamp()
        notifications = self.client.zrangebyscore(
            'scheduled_notifications',
            min=0,
            max=now
        )
        return [json.loads(n) for n in notifications]
    
    def remove_notification(self, notification: Dict):
        """Remove notification from queue"""
        self.client.zrem('scheduled_notifications', json.dumps(notification))
    
    def get_queue_size(self) -> int:
        """Get number of pending notifications"""
        return self.client.zcard('scheduled_notifications')
