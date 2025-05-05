import logging
from datetime import datetime
from sqlmodel import Session, select

from app.models.models import Portfolio, Stock, User, get_engine
from app.services.stock_service import StockService
from app.services.notification_service import NotificationService

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Initialize services
stock_service = StockService()
notification_service = NotificationService()
logger.info("Using NotificationAPI for alerts")

async def check_stock_alerts():
    """
    Background job to check if stocks are near their 200-day moving average
    and send notifications to users if needed.
    """
    logger.info("Running scheduled stock check")
    
    with Session(get_engine()) as session:
        # Get all portfolios
        portfolios = session.exec(select(Portfolio)).all()
        
        for portfolio in portfolios:
            logger.info(f"Checking portfolio: {portfolio.name} (ID: {portfolio.id})")
            
            # Get all stocks in the portfolio
            stocks = session.exec(select(Stock).where(Stock.portfolio_id == portfolio.id)).all()
            
            # Get user info for notifications
            user = session.exec(select(User).where(User.id == portfolio.user_id)).first()
            if not user:
                logger.warning(f"User not found for portfolio {portfolio.id}, skipping")
                continue
            
            for stock in stocks:
                try:
                    # Check if it's time to update this stock based on polling rate
                    should_update = True
                    if stock.last_checked:
                        hours_since_check = (datetime.now() - stock.last_checked).total_seconds() / 3600
                        should_update = hours_since_check >= portfolio.polling_rate
                    
                    if should_update:
                        logger.info(f"Updating stock {stock.symbol}")
                        
                        # Get updated stock data
                        stock_data = await stock_service.get_stock_data(stock.symbol)
                        
                        # Update stock in database
                        stock.last_price = stock_data.get("price", stock.last_price)
                        stock.ma_200 = stock_data.get("ma_200", stock.ma_200)
                        stock.distance_to_ma = stock_data.get("distance_to_ma", stock.distance_to_ma)
                        stock.last_checked = datetime.now()
                        
                        # Check if stock is at or below MA by up to 15%
                        is_at_or_below_ma = False
                        if stock.distance_to_ma is not None and stock.ma_200 is not None:
                            is_at_or_below_ma = (stock.distance_to_ma <= 0 and 
                                                stock.distance_to_ma >= -15.0)
                        
                        # Calculate days since last MA break if we have a break date
                        if stock.last_ma_break_date:
                            days_since_break = (datetime.now() - stock.last_ma_break_date).days
                            stock.days_since_ma_break = days_since_break
                        
                        # If stock just broke MA, record the date
                        if is_at_or_below_ma:
                            # Only update the break date if this is a new break or first time checking
                            if not stock.last_ma_break_date or not stock.notification_sent:
                                stock.last_ma_break_date = datetime.now()
                                stock.days_since_ma_break = 0
                                logger.info(f"Stock {stock.symbol} broke 200-day MA")
                            
                            # Only send notification if it hasn't already been sent for this break
                            if not stock.notification_sent:
                                logger.info(f"Stock {stock.symbol} is at/below 200-day MA, sending notification")
                                
                                # Send notification 
                                success = await notification_service.send_ma_alert(
                                    user.email, 
                                    {
                                        "symbol": stock.symbol,
                                        "price": stock.last_price,
                                        "ma_200": stock.ma_200,
                                        "distance_to_ma": stock.distance_to_ma,
                                        "days_since_break": stock.days_since_ma_break or 0
                                    }
                                )
                                
                                if success:
                                    stock.notification_sent = True
                                    logger.info(f"Notification sent for {stock.symbol}")
                                else:
                                    logger.warning(f"Failed to send notification for {stock.symbol}")
                        
                        # Reset notification flag if stock is no longer at/below MA
                        elif not is_at_or_below_ma and stock.notification_sent:
                            stock.notification_sent = False
                            logger.info(f"Stock {stock.symbol} moved above 200-day MA, reset notification flag")
                        
                        session.add(stock)
                
                except Exception as e:
                    logger.error(f"Error checking stock {stock.symbol}: {str(e)}")
            
            # Commit all changes for this portfolio
            session.commit()
    
    logger.info("Stock check completed")

async def manual_check_portfolio_stocks(portfolio_id: int) -> bool:
    """
    Manually check stocks in a specific portfolio for alerts
    """
    logger.info(f"Manually checking stocks in portfolio {portfolio_id}")
    
    try:
        with Session(get_engine()) as session:
            # Get the portfolio
            portfolio = session.exec(select(Portfolio).where(Portfolio.id == portfolio_id)).first()
            
            if not portfolio:
                logger.error(f"Portfolio {portfolio_id} not found")
                return False
            
            # Get user info for notifications
            user = session.exec(select(User).where(User.id == portfolio.user_id)).first()
            if not user:
                logger.warning(f"User not found for portfolio {portfolio_id}, skipping")
                return False
            
            # Get all stocks in the portfolio
            stocks = session.exec(select(Stock).where(Stock.portfolio_id == portfolio_id)).all()
            
            for stock in stocks:
                try:
                    logger.info(f"Updating stock {stock.symbol}")
                    
                    # Get updated stock data
                    stock_data = await stock_service.get_stock_data(stock.symbol)
                    
                    # IMPORTANT: Only update values if they are not None or zero
                    if stock_data.get("price") and stock_data.get("price") > 0:
                        stock.last_price = stock_data.get("price")
                    
                    if stock_data.get("ma_200") and stock_data.get("ma_200") > 0:
                        stock.ma_200 = stock_data.get("ma_200")
                    
                    if stock_data.get("distance_to_ma") is not None:
                        stock.distance_to_ma = stock_data.get("distance_to_ma")
                        
                    stock.last_checked = datetime.now()
                    
                    # Check if stock is near 200-day MA
                    if stock.last_price and stock.ma_200:
                        is_near_ma = stock_service.is_near_ma(stock.last_price, stock.ma_200, threshold=15.0)
                        
                        # Send notification if stock is near MA and no notification has been sent
                        if is_near_ma and not stock.notification_sent:
                            logger.info(f"Stock {stock.symbol} is near 200-day MA, sending notification")
                            
                            # Send notification 
                            success = await notification_service.send_ma_alert(
                                user.email, 
                                {
                                    "symbol": stock.symbol,
                                    "price": stock.last_price,
                                    "ma_200": stock.ma_200,
                                    "distance_to_ma": stock.distance_to_ma
                                }
                            )
                            
                            if success:
                                stock.notification_sent = True
                                logger.info(f"Notification sent for {stock.symbol}")
                            else:
                                logger.warning(f"Failed to send notification for {stock.symbol}")
                        
                        # Reset notification flag if stock is no longer near MA
                        elif not is_near_ma and stock.notification_sent:
                            stock.notification_sent = False
                            logger.info(f"Stock {stock.symbol} moved away from 200-day MA, reset notification flag")
                    
                    session.add(stock)
                
                except Exception as e:
                    logger.error(f"Error checking stock {stock.symbol}: {str(e)}")
                    # Important: Don't update the stock if there's an error
                    continue
            
            # Commit all changes
            session.commit()
            
        return True
    
    except Exception as e:
        logger.error(f"Error in manual stock check: {str(e)}")
        return False