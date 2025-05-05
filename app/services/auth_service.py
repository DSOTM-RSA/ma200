import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import JWTError, jwt
from fastapi import Cookie, Depends, HTTPException, status
from sqlmodel import Session, select

from app.models.models import User, get_engine

# JWT settings (should be in environment variables in production)
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

def create_access_token(data: Dict) -> str:
    """Generate a JWT token for authentication"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def validate_pin(pin: str) -> bool:
    """Check if a PIN follows the required format (4 letters + 2 digits)"""
    if len(pin) != 6:
        return False
    
    letters = pin[:4]
    digits = pin[4:]
    
    return letters.isalpha() and digits.isdigit()

def get_session():
    with Session(get_engine()) as session:
        yield session

def get_current_user(
    access_token: Optional[str] = Cookie(None, alias="access_token"),
    session: Session = Depends(get_session)
) -> User:
    """Dependency to get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not access_token:
        raise credentials_exception
    
    try:
        # Decode the JWT token
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        pin: str = payload.get("sub")
        if pin is None:
            raise credentials_exception
    
    except JWTError:
        raise credentials_exception
    
    # Get the user from the database
    user = session.exec(select(User).where(User.pin == pin)).first()
    if user is None:
        raise credentials_exception
    
    return user