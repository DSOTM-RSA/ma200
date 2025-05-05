import os
import httpx
from datetime import datetime
from typing import Dict, Optional, Any
import logging

class StockService:
    """Service for interacting with stock market APIs"""
    
    def __init__(self):
        # Using Alpha Vantage API as an example
        # Sign up for a free API key at https://www.alphavantage.co/
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
        self.base_url = "https://www.alphavantage.co/query"

        # Set up logging
        self.logger = logging.getLogger(__name__)
    
    async def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get current stock price and 200-day moving average
        """
        async with httpx.AsyncClient() as client:
            try:
                # Get the SMA (Simple Moving Average)
                params = {
                    "function": "SMA",
                    "symbol": symbol,
                    "interval": "daily",
                    "time_period": 200,
                    "series_type": "close",
                    "apikey": self.api_key
                }
                
                sma_response = await client.get(self.base_url, params=params, timeout=10.0)
                sma_data = sma_response.json()
                
                # Check if we got valid data
                if "Technical Analysis: SMA" not in sma_data:
                    self.logger.warning(f"Invalid SMA data for {symbol}: {sma_data}")
                    # Return None values rather than zeros
                    return {
                        "symbol": symbol,
                        "price": None,
                        "ma_200": None,
                        "distance_to_ma": None,
                        "timestamp": datetime.now()
                    }
                
                # Also get the current quote
                quote_params = {
                    "function": "GLOBAL_QUOTE",
                    "symbol": symbol,
                    "apikey": self.api_key
                }
                
                quote_response = await client.get(self.base_url, params=quote_params, timeout=10.0)
                quote_data = quote_response.json()
                
                # Check if we got valid quote data
                if "Global Quote" not in quote_data or not quote_data["Global Quote"]:
                    self.logger.warning(f"Invalid quote data for {symbol}: {quote_data}")
                    # Return None values rather than zeros
                    return {
                        "symbol": symbol,
                        "price": None,
                        "ma_200": None,
                        "distance_to_ma": None,
                        "timestamp": datetime.now()
                    }
                
                # Extract relevant data
                current_price = float(quote_data.get("Global Quote", {}).get("05. price", 0))
                
                # Make sure we have a valid price
                if current_price <= 0:
                    self.logger.warning(f"Invalid price ({current_price}) for {symbol}")
                    current_price = None
                
                # Get the latest SMA value
                technical_data = sma_data.get("Technical Analysis: SMA", {})
                dates = list(technical_data.keys())
                
                ma_200 = None
                if dates:
                    latest_date = dates[0]
                    try:
                        ma_200 = float(technical_data[latest_date]["SMA"])
                        if ma_200 <= 0:
                            self.logger.warning(f"Invalid MA ({ma_200}) for {symbol}")
                            ma_200 = None
                    except (ValueError, KeyError):
                        self.logger.error(f"Could not parse SMA value for {symbol}")
                
                # Calculate distance to MA (percentage)
                distance_to_ma = None
                if current_price is not None and ma_200 is not None and ma_200 > 0:
                    distance_to_ma = ((current_price - ma_200) / ma_200) * 100
                    distance_to_ma = round(distance_to_ma, 2)
                
                return {
                    "symbol": symbol,
                    "price": current_price,
                    "ma_200": ma_200,
                    "distance_to_ma": distance_to_ma,
                    "timestamp": datetime.now()
                }
                    
            except Exception as e:
                self.logger.error(f"API error for {symbol}: {str(e)}")
                # Don't use mock data in production, return None values instead
                return {
                    "symbol": symbol,
                    "price": None,
                    "ma_200": None,
                    "distance_to_ma": None,
                    "timestamp": datetime.now()
                }
    
    def _get_mock_data(self, symbol: str) -> Dict[str, Any]:
        """Return mock data for demo purposes"""
        import random
        
        # Use realistic price ranges based on the symbol
        # This is just an example, you might want to adjust based on actual stocks
        if symbol in ["AAPL", "MSFT", "AMZN", "GOOGL"]:
            price_base = 150.0
        elif symbol in ["TSLA", "META", "NFLX"]:
            price_base = 250.0
        else:
            price_base = 50.0
        
        # Generate a reasonable price
        price = price_base * random.uniform(0.9, 1.1)
        
        # Generate a moving average that makes sense
        ma_200 = price * random.uniform(0.9, 1.1)
        
        # Calculate distance
        distance_to_ma = ((price - ma_200) / ma_200) * 100
        
        return {
            "symbol": symbol,
            "price": round(price, 2),
            "ma_200": round(ma_200, 2),
            "distance_to_ma": round(distance_to_ma, 2),
            "timestamp": datetime.now()
        }
            
    
    def is_near_ma(self, current_price: float, ma_200: float, threshold: float = 1.0) -> bool:
        """Check if a stock is within threshold% of its 200-day MA"""
        if ma_200 == 0:
            return False
            
        percent_diff = abs((current_price - ma_200) / ma_200 * 100)
        return percent_diff <= threshold