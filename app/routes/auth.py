import re
from fastapi import APIRouter, Request, Depends, HTTPException, Form, status, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from typing import Optional
import logging

from app.models.models import User, get_engine
from app.services.auth_service import create_access_token, validate_pin

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

def get_session():
    with Session(get_engine()) as session:
        yield session

@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register_user(
    request: Request,
    email: str = Form(...),
    pin: str = Form(...),
    session: Session = Depends(get_session)
):
    logger.info(f"Registration attempt with email: {email}, PIN: {pin}")
    
    # Validate PIN format (4 letters + 2 digits)
    if not re.match(r'^[A-Za-z]{4}\d{2}$', pin):
        logger.warning(f"Invalid PIN format: {pin}")
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "error": "PIN must be 4 letters followed by 2 digits"}
        )
    
    # Check if PIN already exists
    existing_user = session.exec(select(User).where(User.pin == pin)).first()
    if existing_user:
        logger.warning(f"PIN already in use: {pin}")
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "error": "PIN already in use"}
        )
    
    # Create new user
    new_user = User(pin=pin, email=email)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    logger.info(f"User created with id: {new_user.id}, email: {email}")
    
    # Create access token (cookie)
    token = create_access_token({"sub": pin})
    
    # Redirect to portfolio page with token cookie
    response = RedirectResponse(url="/portfolio", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=token, httponly=True)
    
    logger.info(f"Redirecting to /portfolio with token set")
    return response

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login_user(
    request: Request,
    pin: str = Form(...),
    session: Session = Depends(get_session)
):
    logger.info(f"Login attempt with PIN: {pin}")
    
    # Validate PIN format
    if not re.match(r'^[A-Za-z]{4}\d{2}$', pin):
        logger.warning(f"Invalid PIN format: {pin}")
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Invalid PIN format"}
        )
    
    # Find user with this PIN
    user = session.exec(select(User).where(User.pin == pin)).first()
    if not user:
        logger.warning(f"No user found with PIN: {pin}")
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Invalid PIN"}
        )
    
    # Create access token (cookie)
    token = create_access_token({"sub": pin})
    
    # Redirect to portfolio page with token cookie
    response = RedirectResponse(url="/portfolio", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=token, httponly=True)
    
    logger.info(f"User logged in successfully with id: {user.id}")
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    logger.info("User logged out")
    return response