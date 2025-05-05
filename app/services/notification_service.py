"""
Notification service for sending alerts using NotificationAPI
"""
import os
import logging
import asyncio
from typing import Dict, Any

# Import NotificationAPI SDK
try:
    from notificationapi_python_server_sdk import notificationapi, EU_REGION
    NOTIFICATION_API_AVAILABLE = True
except ImportError:
    logging.error("NotificationAPI SDK not installed. Run: pip install notificationapi_python_server_sdk")
    raise ImportError("NotificationAPI SDK must be installed to run this application")

class NotificationService:
    """Service for sending notifications via NotificationAPI"""
    
    def __init__(self):
        # Get NotificationAPI credentials from environment variables
        self.client_id = os.getenv("NOTIFICATIONAPI_CLIENT_ID")
        self.client_secret = os.getenv("NOTIFICATIONAPI_CLIENT_SECRET")
        self.notification_id = os.getenv("NOTIFICATIONAPI_NOTIFICATION_ID")
        
        # Initialize NotificationAPI if available and credentials are provided
        if NOTIFICATION_API_AVAILABLE and self.client_id and self.client_secret:
            # Use EU_REGION constant instead of a URL string
            notificationapi.init(self.client_id, self.client_secret, EU_REGION)
            logging.info("NotificationAPI initialized successfully")
        else:
            logging.error("NotificationAPI credentials not set. Check environment variables.")
            raise ValueError("NotificationAPI credentials must be provided")
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
    
    async def send_ma_alert(self, user_email: str, stock_data: Dict[str, Any]) -> bool:
        """
        Send a stock alert notification using NotificationAPI
        
        Args:
            user_email: Email address to send the alert to
            stock_data: Dictionary containing stock info
            
        Returns:
            bool: True if notification was sent successfully, False otherwise
        """
        # Format the comment/message for the notification template
        message = (
            f"Stock Alert: {stock_data['symbol']} is near its 200-day Moving Average\n\n"
            f"• Symbol: {stock_data['symbol']}\n"
            f"• Current Price: ${stock_data['price']:.2f}\n"
            f"• 200-day MA: ${stock_data['ma_200']:.2f}\n"
            f"• Distance to MA: {stock_data['distance_to_ma']:.2f}%\n\n"
            f"The 200-day moving average is a key technical indicator used by traders and investors "
            f"to identify potential market trends and support/resistance levels."
        )
        
        # Try to send the notification
        try:
            # Set up the payload for NotificationAPI
            payload = {
                "notificationId": self.notification_id,
                "user": {
                    "id": user_email,  # Using email as the user ID for simplicity
                    "email": user_email
                },
                "mergeTags": {
                    "symbol": stock_data['symbol'],
                    "price": f"${stock_data['price']:.2f}",
                    "ma_200": f"${stock_data['ma_200']:.2f}",
                    "distance": f"{stock_data['distance_to_ma']:.2f}%"
                }
            }
            
            # Send the notification
            await notificationapi.send(payload)
            
            self.logger.info(f"Notification sent to {user_email} for stock {stock_data['symbol']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send notification to {user_email}: {str(e)}")
            return False
    
    async def send_test_notification(self, user_email: str) -> bool:
        """
        Send a test notification using NotificationAPI
        
        Args:
            user_email: Email address to send the test to
            
        Returns:
            bool: True if notification was sent successfully, False otherwise
        """
        # Try to send the test notification
        try:
            # Set up the payload for NotificationAPI
            payload = {
                "notificationId": self.notification_id,
                "user": {
                    "id": user_email,
                    "email": user_email
                },
                "mergeTags": {
                    "symbol": "AAPL",
                    "price": "$184.25",
                    "ma_200": "$180.50",
                    "distance": "2.08%"
                }
            }
            
            # Send the notification
            await notificationapi.send(payload)
            
            self.logger.info(f"Test notification sent to {user_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send test notification to {user_email}: {str(e)}")
            return False