# Product Context: Stock Portfolio Monitoring Application

## Purpose

This application provides a lightweight and easy-to-maintain solution for monitoring stock portfolios. It aims to help users track their investments and receive timely alerts when stocks approach their 200-day moving average (MA).

## How It Works

1.  **User Registration/Login:** Users register with an email and a unique PIN. They can then log in to access their portfolio.
2.  **Portfolio Creation:** Users create portfolios and specify a polling rate (how often to check stock prices).
3.  **Stock Addition:** Users add stocks to their portfolio using ticker symbols.
4.  **Automated Monitoring:** The application automatically fetches stock data from the Alpha-Vantage API and monitors the distance to the 200-day MA.
5.  **Alerts:** When a stock approaches its 200-day MA, the user receives a notification.

## Problems Solved

*   **Manual Tracking:** Automates the tedious process of manually tracking stock prices and calculating the 200-day MA.
*   **Missed Opportunities:** Helps users avoid missing potential buying or selling opportunities by providing timely alerts.
*   **Lack of Visibility:** Provides a clear overview of the portfolio's performance and the status of individual stocks.
*   **Complexity:** Offers a simple and easy-to-use interface, avoiding the complexity of more advanced trading platforms.
