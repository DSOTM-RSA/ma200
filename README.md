# MA200: The Only Wave You Need to Ride

A lightweight stock portfolio tracker that alerts you when stocks approach their 200-day moving average.

## Motivation

The primary goal of this project is to offer a lightweight, user-friendly application designed for monitoring stock portfolios. Our specific focus is on alerting users when their stocks approach or cross the 200-day moving average (MA), a key technical indicator used by many traders and investors.

This application addresses several key challenges faced by investors:

*   **Automation of Manual Tracking:** It automates the otherwise tedious and time-consuming manual process of continuously tracking individual stock prices against their 200-day MA.
*   **Identification of Opportunities:** By providing timely alerts, the application helps users identify potential buying or selling opportunities that may arise when a stock's price interacts with this significant moving average.
*   **Simplicity and Clarity:** It offers a clear and simple overview of portfolio performance in relation to the 200-day MA, deliberately avoiding the often overwhelming complexity found in more comprehensive trading platforms.

Ultimately, this tool aims to empower users by providing actionable insights with minimal effort, allowing them to make more informed decisions about their stock holdings.

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

## Architecture

This section outlines the system architecture, detailing the components and their interactions to provide a clear understanding of how the application functions.

*   **Frontend**: The user interface is built using HTML templates that are directly rendered by the backend. Client-side interactions are enhanced using HTMX and Hyperscript. This approach minimizes the need for extensive JavaScript, keeping the frontend lightweight and straightforward while still enabling dynamic user experiences.

*   **Backend**: The core of the application is a Python-based API developed with FastAPI. It is responsible for all business logic, including user authentication, portfolio management, stock data processing, and serving the HTML templates to the client.

*   **Database**: SQLite is utilized as the database for storing user data, portfolio information, and stock details. SQLModel is used as the Object-Relational Mapper (ORM) for database interactions, chosen for its simplicity, ease of integration, and Pythonic feel.

*   **Authentication**: User authentication is managed through a simple PIN-based system. Upon successful login, JSON Web Tokens (JWT) are issued to secure user sessions and authenticate subsequent requests to protected endpoints.

*   **Background Processing**: Periodic tasks, primarily the polling of stock data from the Alpha-Vantage API, are handled by APScheduler. Users can configure the polling intervals, and APScheduler ensures that stock information is updated regularly in the background without direct user intervention.

*   **Notifications**: The application integrates with NotificationAPI to dispatch alerts. When a monitored stock meets specific criteria, such as crossing its 200-day moving average, the backend triggers a notification via NotificationAPI to inform the user.

*   **Deployment**: The application is designed to be Dockerized. This containerization approach simplifies the deployment process, allowing it to be easily deployed on various cloud platforms or any environment that supports Docker.

## Tech Stack

The project employs a modern Python-based stack. For a detailed breakdown of the technologies used and how they interact, please see the Architecture section.

## Getting Started

1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables for NotificationAPI
4. Run: `uvicorn app.main:app --reload`
