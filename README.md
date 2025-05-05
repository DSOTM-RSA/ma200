# MA200: The Only Wave You Need to Ride

A lightweight stock portfolio tracker that alerts you when stocks approach their 200-day moving average.

## Tech Stack

* **Backend**: Python with FastAPI
* **Frontend**: HTML templates with HTMX and Hyperscript
* **Database**: SQLite with SQLModel
* **Authentication**: Simple PIN-based auth with JWT tokens
* **Notifications**: NotificationAPI
* **Background Tasks**: APScheduler
* **HTTP Client**: HTTPX for async API calls

## Features

* **Simple Authentication**: Register and login with email and PIN
* **Portfolio Management**: Create a portfolio and add/remove stocks
* **Stock Monitoring**: Track stock prices relative to 200-day moving average
* **Automated Checks**: Configurable polling rate for stock data updates
* **MA Break Alerts**: Get notified when stocks cross their 200-day MA
* **Days Tracking**: See how long stocks have been below their MA
* **Manual Controls**: Force refresh and check stocks manually
* **Test Notifications**: Verify your notification setup works
* **Responsive Design**: Works on desktop and mobile devices

## Getting Started

1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables for NotificationAPI
4. Run: `uvicorn app.main:app --reload`
