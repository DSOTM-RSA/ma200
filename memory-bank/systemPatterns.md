# System Architecture and Design Patterns

## Overview

This document outlines the key architectural components, technical decisions, and design patterns employed in the stock portfolio monitoring application.

## Architecture

*   **Backend:** FastAPI
*   **Frontend:** HTML/CSS with HTMX/hyperscript
*   **Database:** SQLite
*   **Deployment:** Dockerized, targeting Azure Container Apps and/or Google Cloud Platform

## Key Technical Decisions

*   **Language:** Python for backend development.
*   **Frontend Interactivity:** HTMX/hyperscript for dynamic updates without JavaScript.
*   **Database Choice:** SQLite for lightweight storage.
*   **API Integration:** Alpha-Vantage API for stock data.
*   **Notification Service:** 3rd party service for sending notifications.

## Design Patterns

*   **Model-View-Controller (MVC):** Applied through FastAPI routes (controllers), HTML templates (views), and models for data representation.
*   **Dependency Injection:** Used within the FastAPI application for managing dependencies.
*   **Observer Pattern:** Used for monitoring stock data and triggering notifications.
