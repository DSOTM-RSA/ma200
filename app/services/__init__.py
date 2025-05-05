"""
Services for the Stock Portfolio Tracker application.

This package includes:
- auth_service: User authentication and authorization
- stock_service: Stock data retrieval and processing
- email_service: Email notification functionality
- notification_service: NotificationAPI integration for alerts
"""

from app.services.auth_service import create_access_token, validate_pin, get_current_user
from app.services.stock_service import StockService
from app.services.notification_service import NotificationService

__all__ = [
    "create_access_token", 
    "validate_pin", 
    "get_current_user",
    "StockService",
    "NotificationService"
]