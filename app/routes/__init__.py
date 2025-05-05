
"""
API routes for the Stock Portfolio Tracker application.

This package includes:
- auth: Authentication and user management routes
- portfolio: Portfolio and stock management routes
"""

from app.routes import auth, portfolio

__all__ = ["auth", "portfolio"]