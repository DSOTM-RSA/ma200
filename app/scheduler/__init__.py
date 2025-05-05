"""
Background job scheduler for the Stock Portfolio Tracker application.

This package handles the scheduling and execution of periodic tasks
such as checking stock prices and sending notifications.
"""

__all__ = ["check_stock_alerts"]
# Don't import the function here to avoid circular imports