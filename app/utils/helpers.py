"""
Helper functions for the Stock Portfolio Tracker application.
"""
import re
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Union, List

def format_currency(value: Union[float, int, None]) -> str:
    """Format a value as currency with 2 decimal places"""
    if value is None:
        return "$0.00"
    return f"${value:.2f}"

def format_percentage(value: Union[float, int, None]) -> str:
    """Format a value as percentage with 2 decimal places"""
    if value is None:
        return "0.00%"
    return f"{value:.2f}%"

def format_datetime(dt: Optional[datetime]) -> str:
    """Format a datetime in a user-friendly format"""
    if dt is None:
        return "Never"
    # Convert to local timezone
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = now - dt
    
    if diff.days == 0:
        # Today
        if diff.seconds < 60:
            return "Just now"
        elif diff.seconds < 3600:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return f"{diff.seconds // 3600} hours ago"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    else:
        return dt.strftime("%b %d, %Y")

def validate_stock_symbol(symbol: str) -> bool:
    """
    Validate a stock symbol format (1-5 uppercase letters)
    
    Most stock symbols are 1-5 uppercase letters, though some
    may include additional characters for special cases.
    """
    return bool(re.match(r'^[A-Z]{1,5}$', symbol))

def validate_pin(pin: str) -> bool:
    """
    Validate a PIN format (4 letters + 2 digits)
    """
    return bool(re.match(r'^[A-Za-z]{4}\d{2}$', pin))

def truncate_string(text: str, max_length: int = 50) -> str:
    """Truncate a string to a maximum length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def get_env_variable(name: str, default: Any = None) -> Any:
    """
    Get an environment variable or return a default value
    
    Args:
        name: Name of the environment variable
        default: Default value if the environment variable is not set
        
    Returns:
        The value of the environment variable or the default
    """
    return os.environ.get(name, default)

def calculate_ma_status(price: Optional[float], ma_200: Optional[float]) -> Dict[str, Any]:
    """
    Calculate the status of a stock relative to its 200-day MA
    
    Args:
        price: Current stock price
        ma_200: 200-day moving average
        
    Returns:
        Dictionary with status information
    """
    if price is None or ma_200 is None or ma_200 == 0:
        return {
            "status": "unknown",
            "label": "Unknown",
            "color": "gray",
            "distance": None
        }
    
    distance = ((price - ma_200) / ma_200) * 100
    
    if abs(distance) < 1:
        return {
            "status": "at_ma",
            "label": "At MA",
            "color": "orange",
            "distance": distance
        }
    elif distance > 0:
        return {
            "status": "above_ma",
            "label": "Above MA",
            "color": "green",
            "distance": distance
        }
    else:
        return {
            "status": "below_ma",
            "label": "Below MA",
            "color": "red",
            "distance": distance
        }

def generate_random_pin() -> str:
    """Generate a random PIN (4 letters + 2 digits)"""
    import random
    import string
    
    letters = ''.join(random.choices(string.ascii_letters, k=4))
    digits = ''.join(random.choices(string.digits, k=2))
    
    return f"{letters}{digits}"