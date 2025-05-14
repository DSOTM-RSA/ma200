# Technical Context

## Overview

This document provides an overview of the packages and technologies used in the stock portfolio monitoring application.

## Technologies

*   **Programming Language:** Python
*   **Web Framework:** FastAPI
*   **Frontend:** HTML/CSS with HTMX/hyperscript
*   **Database:** SQLite
*   **Deployment:** Docker

## Packages

*   fastapi>=0.104.1
*   uvicorn>=0.24.0
*   python-multipart>=0.0.6  # For form data processing
*   sqlmodel>=0.0.8
*   sqlalchemy>=2.0.23
*   alembic>=1.12.1  # For database migrations
*   aiosqlite>=0.19.0  # For async SQLite support
*   jinja2>=3.1.2
*   python-jose>=3.3.0  # For JWT tokens
*   passlib>=1.7.4  # For password hashing
*   bcrypt>=4.0.1  # For password hashing
*   python-jose[cryptography]>=3.3.0
*   passlib[bcrypt]>=1.7.4
*   python-dotenv>=1.0.0  # For environment variables
*   httpx>=0.25.1  # Asynchronous HTTP client
*   APScheduler>=3.10.4
*   notificationapi_python_server_sdk>=0.2.10
*   pytest>=7.4.3
*   pytest-asyncio>=0.21.1
*   gunicorn>=21.2.0  # For production server
*   uvicorn[standard]>=0.24.0  # For production-ready ASGI server
