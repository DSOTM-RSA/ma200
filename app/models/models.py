from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel, create_engine
import os
from datetime import datetime

# Create SQLite database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stock_tracker.db")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pin: str = Field(index=True, unique=True)  # 4 letters + 2 digits
    email: str
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    portfolios: List["Portfolio"] = Relationship(back_populates="user")


class Portfolio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    polling_rate: int = Field(default=24)  # Hours between checks
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="portfolios")
    stocks: List["Stock"] = Relationship(back_populates="portfolio")


class Stock(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str
    portfolio_id: Optional[int] = Field(default=None, foreign_key="portfolio.id")
    last_price: Optional[float] = None
    ma_200: Optional[float] = None
    distance_to_ma: Optional[float] = None
    last_checked: Optional[datetime] = None
    notification_sent: bool = Field(default=False)
    # New fields
    last_ma_break_date: Optional[datetime] = None  # When the stock last broke the MA
    days_since_ma_break: Optional[int] = None  # Calculated field
    
    # Relationships
    portfolio: Optional[Portfolio] = Relationship(back_populates="stocks")


# Create the engine
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_engine():
    return engine