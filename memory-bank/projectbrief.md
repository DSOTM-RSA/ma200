# High Level Overview

I am building a simply stock-portfolio monitoring application. It is consists of monitoring the 200 Day Moving-Average (MA) of the portfolio stocks by polling a free Alpha-Vantage API at a given interval.

When the 200-Day-MA is reached or crossed (<0%) difference then a notification is sent to the user via a 3rd party service. 

# Core Requirements

- build a very lightweight, easy to maintain and simply dockerized web-application
- use the preferred tech stack of Python + HTML/CSS 
- FastAPI for the backend
- HTMX/hyperscript for interactivtiy and passing context to the backend routes
- sqlite for database storage
- does not use JS
- a Dockerized application
- target deployment to Azure Container Apps and/or Google Cloud Platform