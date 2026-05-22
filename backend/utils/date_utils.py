from datetime import datetime, timedelta
from typing import List

def get_weekdays_between(start_date: datetime, end_date: datetime) -> int:
    """Count weekdays between two dates"""
    count = 0
    current = start_date
    while current < end_date:
        if current.weekday() < 5:  # Monday-Friday
            count += 1
        current += timedelta(days=1)
    return count

def is_weekend(date: datetime) -> bool:
    """Check if date is weekend"""
    return date.weekday() >= 5

def get_next_weekday(date: datetime) -> datetime:
    """Get next weekday from given date"""
    next_day = date + timedelta(days=1)
    while next_day.weekday() >= 5:
        next_day += timedelta(days=1)
    return next_day

def format_time_slot(hour: int, minute: int = 0) -> str:
    """Format time as HH:MM"""
    return f"{hour:02d}:{minute:02d}"
