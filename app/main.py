import os
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from contextlib import asynccontextmanager
from datetime import datetime
import logging

from app.models.models import create_db_and_tables, get_engine, User, Portfolio, Stock
from app.services.stock_service import StockService
from app.services.notification_service import NotificationService
from app.routes import auth, portfolio

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# App startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup: Create DB tables and start scheduler
    create_db_and_tables()
    scheduler = BackgroundScheduler()
    
    # Import the check_stock_alerts function here to avoid circular imports
    try:
        from app.scheduler.jobs import check_stock_alerts
        
        # Add job to check stocks every hour
        scheduler.add_job(
            check_stock_alerts,
            trigger=IntervalTrigger(hours=1),
            id="stock_checker",
            replace_existing=True,
        )
        
        logger.info("Scheduled stock checker job")
    except ImportError as e:
        logger.error(f"Could not import check_stock_alerts: {str(e)}")
        logger.warning("Stock checking scheduler not started")
    
    scheduler.start()
    yield
    # Shutdown: Stop scheduler
    scheduler.shutdown()

# Create FastAPI app
app = FastAPI(lifespan=lifespan)

# Set up static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(portfolio.router)

# Dependency for DB sessions
def get_session():
    with Session(get_engine()) as session:
        yield session

# Root route
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)