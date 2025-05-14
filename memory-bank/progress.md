# Project Progress

## Overview

This document tracks the progress of the stock portfolio monitoring application, summarizing key aspects of the backend and frontend code.

## Backend

*   **Key Files:**
    *   `app/main.py`: Sets up the FastAPI application, including routers, middleware, and a background scheduler for stock alerts.
    *   `app/routes/auth.py`: Handles user registration, login, and logout using PIN-based authentication.
    *   `app/routes/portfolio.py`: Manages portfolio creation, stock addition/removal, and refreshing stock data, including sending test notifications.

## Frontend

*   **Key Files:**
    *   `app/static/js/app.js`: Contains JavaScript for auto-dismissing flash messages, PIN validation, form submission with PIN validation, and optional periodic refresh of the portfolio page.
    *   `app/templates/index.html`: The homepage template, including a welcome message, links for login/registration, a "How It Works" section, and custom CSS.
    *   `app/templates/portfolio.html`: The portfolio page template, including portfolio details, stock information, and forms for portfolio management.
