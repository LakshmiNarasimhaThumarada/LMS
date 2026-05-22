import logging
import os
from datetime import datetime

# Ensure log directory exists
LOG_DIR = '/var/log/edumind'
if not os.path.exists(LOG_DIR):
    # Fallback to current directory if system log dir is not accessible
    LOG_DIR = './logs'
    os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'app.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('edumind')

def log_api_call(endpoint: str, user_id: str, duration_ms: float):
    """Log API call for monitoring"""
    logger.info(f"API: {endpoint} | User: {user_id} | Duration: {duration_ms}ms")

def log_agent_execution(agent_name: str, duration_sec: float, success: bool):
    """Log LangGraph agent execution"""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"Agent: {agent_name} | Duration: {duration_sec}s | Status: {status}")

def log_notification_sent(user_id: str, channel: str, success: bool):
    """Log notification delivery"""
    status = "SENT" if success else "FAILED"
    logger.info(f"Notification: {channel} | User: {user_id} | Status: {status}")

def log_error(module: str, error_msg: str):
    """Log general errors"""
    logger.error(f"Error in {module}: {error_msg}")
