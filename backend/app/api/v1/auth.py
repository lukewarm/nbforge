from datetime import timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from pydantic import ValidationError
import logging

from app import crud, schemas
from app.models.user import User
from app.api import deps
from app.core import security
from app.core.config import get_settings

settings = get_settings()
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/login", response_model=schemas.Token)
async def login(
    request: Request,
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    Supports remember_me parameter for longer session duration.
    """
    # Try to get the remember_me flag from the request body
    remember_me = False
    
    # Check if this is a JSON request with remember_me
    try:
        body = await request.json()
        remember_me = body.get("remember_me", False)
        
        # If this is a JSON request, get username and password from JSON
        if "username" in body and "password" in body:
            username = body["username"]
            password = body["password"]
        else:
            # Otherwise use form data
            username = form_data.username
            password = form_data.password
    except:
        # Not a JSON request, use form data
        username = form_data.username
        password = form_data.password
    
    # Authenticate the user
    user = crud.user.authenticate(db, email=username, password=password)
    
    if not user:
        # Demo mode: allow any login with specific usernames
        if settings.DEMO_MODE and username in [settings.DEMO_USER]:
            user = crud.user.get_by_email(db, email=username)
            if not user:
                # Create demo user if it doesn't exist
                user_in = schemas.UserCreate(
                    email=username,
                    password="demo",  # Will be hashed
                    is_active=True,
                )
                user = crud.user.create(db, obj_in=user_in)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Use a longer expiration time if remember_me is True
    if remember_me:
        access_token_expires = timedelta(days=31)  # 31 days for "remember me"
    else:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=schemas.User)
def register(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Create new user.
    """
    # Check if email already exists
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )
    
    # Check if username already exists (if username is provided)
    if user_in.username:
        existing_user = crud.user.get_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this username already exists",
            )
    
    user = crud.user.create(db, obj_in=user_in)
    return user

@router.get("/config", response_model=Dict[str, Any])
def get_auth_config():
    """
    Get authentication configuration for the frontend
    """
    return {
        "oauth_providers": {
            "google": {
                "client_id": bool(settings.OAUTH_PROVIDERS.get("google", {}).get("client_id")),
                "enabled": bool(settings.OAUTH_PROVIDERS.get("google", {}).get("client_id"))
            },
            "github": {
                "client_id": bool(settings.OAUTH_PROVIDERS.get("github", {}).get("client_id")),
                "enabled": bool(settings.OAUTH_PROVIDERS.get("github", {}).get("client_id"))
            }
        },
        "demo_mode": settings.DEMO_MODE,
        "demo_user": settings.DEMO_USER if settings.DEMO_MODE else None,
        "emails_enabled": settings.EMAILS_ENABLED and settings.EMAIL_PROVIDER != "dummy"
    }

async def get_demo_token():
    """Get a token for the demo user"""
    if not settings.DEMO_MODE:
        return None
        
    # Create or get demo user
    db = next(deps.get_db())
    user = crud.user.get_by_email(db, email=settings.DEMO_USER)
    
    if not user:
        # Create a new demo user with is_active=True
        user_in = schemas.UserCreate(
            email=settings.DEMO_USER,
            password=security.create_callback_token(),  # Generate a random password
            is_active=True,
            full_name="Demo User"
        )
        user = crud.user.create(db, obj_in=user_in)
    elif not user.is_active:
        # Ensure demo user is always active
        user.is_active = True
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.get("/demo-token", response_model=schemas.Token)
async def demo_token():
    """
    Get a demo user token when in demo mode
    """
    if not settings.DEMO_MODE:
        logging.warning("Demo token endpoint accessed when demo mode is disabled")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo mode is not enabled"
        )
    
    token = await get_demo_token()
    if not token:
        logging.error("Failed to generate demo token")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate demo token"
        )
    
    logging.info("Successfully provided demo token")
    return token

@router.get("/me", response_model=schemas.User)
async def read_users_me(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_current_user)
) -> Any:
    """
    Get current user. In demo mode, automatically creates and returns demo user.
    """
    # If we have a user, just return it
    if current_user:
        return current_user
        
    # For demo mode, try to get demo user
    if settings.DEMO_MODE:
        # Try to create/get demo user and token
        token_data = await get_demo_token()
        if token_data:
            user_id = security.decode_access_token(token_data["access_token"])
            user = crud.user.get(db, id=user_id)
            if user:
                return user
    
    # No user found
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated"
    )

# OAuth endpoints for Google, GitHub, etc.
@router.get("/oauth/google")
def login_google():
    """
    Generate Google OAuth login URL
    """
    # Implementation depends on the OAuth library used
    pass

@router.get("/oauth/google/callback")
def google_callback(code: str, db: Session = Depends(deps.get_db)):
    """
    Handle Google OAuth callback
    """
    # Implementation depends on the OAuth library used
    pass 

@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password(
    email_data: dict,
    db: Session = Depends(deps.get_db)
):
    """
    Send a password reset email.
    """
    logger = logging.getLogger(__name__)
    
    email = email_data.get("email")
    logger.info(f"Password reset requested for email: {email}")
    
    if not email:
        logger.error("Email is required for password reset")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required"
        )
        
    user = crud.user.get_by_email(db, email=email)
    
    # Always return 204 even if user doesn't exist to prevent user enumeration
    if not user:
        logger.info(f"Password reset requested for non-existent email: {email}")
        # No response body with 204 status code, so message will only be in logs
        return
    
    logger.info(f"Generating password reset token for user ID: {user.id}")
    # Create password reset token (expires in 24 hours)
    token_expires = timedelta(hours=24)
    
    # Generate a clean token with just the necessary claims
    password_reset_token = security.create_access_token(
        subject=str(user.id),
        expires_delta=token_expires,
        data={"reset": True}
    )
    
    logger.info(f"Password reset token generated: {password_reset_token[:10]}...")
    
    # Send password reset email
    from app.services.email.email import email_service
    
    reset_link = f"{settings.FRONTEND_URL}/#/reset-password?token={password_reset_token}"
    logger.info(f"Password reset link (truncated): {reset_link[:50]}...")
    
    await email_service.send_password_reset_email(
        email_to=user.email,
        token=password_reset_token
    )
    
    logger.info(f"Password reset email sent to: {email}")
    return

@router.post("/reset-password", response_model=schemas.User)
async def reset_password(
    reset_data: dict,
    db: Session = Depends(deps.get_db)
):
    """
    Reset password using a token.
    """
    logger = logging.getLogger(__name__)
    
    token = reset_data.get("token")
    new_password = reset_data.get("new_password")
    
    logger.info("Reset password request received")
    
    if not token or not new_password:
        logger.error("Token or new password missing")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token and new password are required"
        )
        
    try:
        logger.info("Attempting to decode token")
        
        # Use the security module's decode function directly
        try:
            payload = security.decode_access_token(token)
        except HTTPException as e:
            # Handle the HTTPException thrown by decode_access_token
            logger.error(f"Token validation failed: {e.detail}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token. Please request a new password reset link."
            )
        
        if not payload or not payload.get("reset"):
            logger.error("Token validation failed: reset claim missing")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token. Please request a new password reset link."
            )
            
        user_id = payload["sub"]
        logger.info(f"Looking up user with ID: {user_id}")
        user = crud.user.get(db, id=user_id)
        
        if not user:
            logger.error("User not found for provided token")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # Update user's password
        logger.info(f"Updating password for user")
        
        try:
            # Hash the password and update directly
            hashed_password = security.get_password_hash(new_password)
            user.hashed_password = hashed_password
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info("Password successfully updated")
            return user
        except Exception as e:
            # Ensure we don't expose sensitive info in error messages
            logger.error(f"Error updating password: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating password. Please try again later."
            )
    except Exception as e:
        # Catch any other unexpected exceptions
        logger.error(f"Unexpected error in reset_password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        ) 