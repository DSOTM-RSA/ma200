from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from typing import List, Optional
import logging

from app.models.models import User, Portfolio, Stock, get_engine
from app.services.auth_service import get_current_user
from app.services.stock_service import StockService

router = APIRouter(tags=["portfolio"])
templates = Jinja2Templates(directory="app/templates")
stock_service = StockService()
logger = logging.getLogger(__name__)

def get_session():
    with Session(get_engine()) as session:
        yield session

@router.get("/portfolio")
async def portfolio_page(
    request: Request,
    error: str = None,
    success: str = None,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Get existing portfolio for the user
    portfolio = session.exec(
        select(Portfolio).where(Portfolio.user_id == user.id)
    ).first()
    
    # If no portfolio exists, show portfolio creation form
    has_portfolio = portfolio is not None
    
    portfolio_with_stocks = None
    if has_portfolio:
        # Get all stocks in portfolio
        stocks = session.exec(
            select(Stock).where(Stock.portfolio_id == portfolio.id)
        ).all()
        
        portfolio_with_stocks = {
            "id": portfolio.id,
            "name": portfolio.name,
            "polling_rate": portfolio.polling_rate,
            "stocks": stocks
        }
    
    # Handle notification errors/success
    error_message = None
    success_message = None
    
    if error == "notification_failed":
        error_message = "Failed to send test notification. Please check your NotificationAPI setup."
    elif error == "email_failed":
        error_message = "Failed to send test email. Please check your email service setup."
    
    if success == "notification_sent":
        success_message = "Test notification was sent successfully. Please check your email."
    elif success == "check_completed":
        success_message = "Stock alerts check completed successfully."
    
    return templates.TemplateResponse(
        "portfolio.html", 
        {
            "request": request, 
            "user": user, 
            "has_portfolio": has_portfolio,
            "portfolio": portfolio_with_stocks,
            "error": error_message,
            "success": success_message
        }
    )

@router.post("/portfolio/create")
async def create_portfolio(
    request: Request,
    name: str = Form(...),
    polling_rate: int = Form(24),  # Default to 24 hours
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Check if user already has a portfolio
    existing_portfolio = session.exec(
        select(Portfolio).where(Portfolio.user_id == user.id)
    ).first()
    
    if existing_portfolio:
        logger.warning(f"User {user.id} attempted to create a second portfolio")
        return templates.TemplateResponse(
            "portfolio.html", 
            {
                "request": request, 
                "user": user, 
                "error": "You already have a portfolio"
            }
        )
    
    # Create new portfolio
    new_portfolio = Portfolio(name=name, polling_rate=polling_rate, user_id=user.id)
    session.add(new_portfolio)
    session.commit()
    logger.info(f"Created new portfolio '{name}' for user {user.id}")
    
    return RedirectResponse(url="/portfolio", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/portfolio/{portfolio_id}/add-stock")
async def add_stock(
    request: Request,
    portfolio_id: int,
    symbol: str = Form(...),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify portfolio exists and belongs to user
    portfolio = session.exec(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        )
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Verify stock symbol exists by calling the API
    try:
        stock_data = await stock_service.get_stock_data(symbol)
        if not stock_data:
            return templates.TemplateResponse(
                "portfolio.html", 
                {
                    "request": request, 
                    "user": user, 
                    "error": f"Stock symbol '{symbol}' not found"
                }
            )
    except Exception as e:
        return templates.TemplateResponse(
            "portfolio.html", 
            {
                "request": request, 
                "user": user, 
                "error": f"Error checking stock: {str(e)}"
            }
        )
    
    # Check if stock already exists in portfolio
    existing = session.exec(
        select(Stock).where(
            Stock.portfolio_id == portfolio_id,
            Stock.symbol == symbol.upper()
        )
    ).first()
    
    if existing:
        return templates.TemplateResponse(
            "portfolio.html", 
            {
                "request": request, 
                "user": user, 
                "error": f"Stock {symbol} already in portfolio"
            }
        )
    
    # Add stock to portfolio
    new_stock = Stock(
        symbol=symbol.upper(),
        portfolio_id=portfolio_id,
        last_price=stock_data.get("price", 0),
        ma_200=stock_data.get("ma_200", 0),
        distance_to_ma=stock_data.get("distance_to_ma", 0),
    )
    
    session.add(new_stock)
    session.commit()
    logger.info(f"Added stock {symbol.upper()} to portfolio {portfolio_id}")
    
    return RedirectResponse(url="/portfolio", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/portfolio/{portfolio_id}/remove-stock/{stock_id}")
async def remove_stock(
    portfolio_id: int,
    stock_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify portfolio exists and belongs to user
    portfolio = session.exec(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        )
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Find and delete the stock
    stock = session.exec(
        select(Stock).where(
            Stock.id == stock_id,
            Stock.portfolio_id == portfolio_id
        )
    ).first()
    
    if stock:
        symbol = stock.symbol
        session.delete(stock)
        session.commit()
        logger.info(f"Removed stock {symbol} from portfolio {portfolio_id}")
    
    return RedirectResponse(url="/portfolio", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/portfolio/{portfolio_id}/delete")
async def delete_portfolio(
    portfolio_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify portfolio exists and belongs to user
    portfolio = session.exec(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        )
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Delete all stocks in portfolio
    stocks = session.exec(
        select(Stock).where(Stock.portfolio_id == portfolio_id)
    ).all()
    
    for stock in stocks:
        session.delete(stock)
    
    # Delete portfolio
    portfolio_name = portfolio.name
    session.delete(portfolio)
    session.commit()
    logger.info(f"Deleted portfolio {portfolio_name} for user {user.id}")
    
    return RedirectResponse(url="/portfolio", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/portfolio/{portfolio_id}/refresh")
async def refresh_portfolio(
    portfolio_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify portfolio exists and belongs to user
    portfolio = session.exec(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        )
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Get all stocks in portfolio
    stocks = session.exec(
        select(Stock).where(Stock.portfolio_id == portfolio_id)
    ).all()
    
    # Update each stock
    for stock in stocks:
        try:
            stock_data = await stock_service.get_stock_data(stock.symbol)
            if stock_data:
                stock.last_price = stock_data.get("price", stock.last_price)
                stock.ma_200 = stock_data.get("ma_200", stock.ma_200)
                stock.distance_to_ma = stock_data.get("distance_to_ma", stock.distance_to_ma)
                stock.last_checked = stock_data.get("timestamp", None)
                session.add(stock)
        except Exception as e:
            logger.error(f"Error updating stock {stock.symbol}: {str(e)}")
            continue
    
    session.commit()
    logger.info(f"Refreshed portfolio {portfolio_id}")
    
    return RedirectResponse(url="/portfolio", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/portfolio/{portfolio_id}/test-notification")
async def test_notification(
    portfolio_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Send a test notification to the user"""
    # Verify portfolio exists and belongs to user
    portfolio = session.exec(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        )
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Use the NotificationService
    from app.services.notification_service import NotificationService
    notification_service = NotificationService()
    success = await notification_service.send_test_notification(user.email)
    
    if success:
        logger.info(f"Test notification sent to {user.email}")
        return RedirectResponse(
            url="/portfolio?success=notification_sent", 
            status_code=status.HTTP_303_SEE_OTHER,
        )
    else:
        logger.error(f"Failed to send test notification to {user.email}")
        return RedirectResponse(
            url="/portfolio?error=notification_failed", 
            status_code=status.HTTP_303_SEE_OTHER
        )
        
@router.get("/portfolio/{portfolio_id}/check-alerts")
async def manual_check_alerts(
    portfolio_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Manually trigger the stock alerts check for this portfolio"""
    # Verify portfolio exists and belongs to user
    portfolio = session.exec(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        )
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Import the check function
    from app.scheduler.jobs import manual_check_portfolio_stocks
    
    # Run the check for this specific portfolio
    success = await manual_check_portfolio_stocks(portfolio_id)
    
    if success:
        logger.info(f"Manual stock check completed for portfolio {portfolio_id}")
        return RedirectResponse(
            url="/portfolio?success=check_completed", 
            status_code=status.HTTP_303_SEE_OTHER
        )
    else:
        logger.error(f"Error running manual stock check for portfolio {portfolio_id}")
        return RedirectResponse(
            url="/portfolio?error=check_failed", 
            status_code=status.HTTP_303_SEE_OTHER
        )