from typing import Generator, Optional, Union

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud
from app import schemas
from app.models.user import User
from app.models.service_account import ServiceAccount
from app.core import security
from app.core.config import get_settings
from app.db.session import SessionLocal

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_name_header = APIKeyHeader(name="X-API-Key-Name", auto_error=False)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    try:
        # Decode the token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
        
        # Get the user
        user = crud.user.get(db, id=token_data.sub)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
            
        return user
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user

async def get_service_account(
    db: Session = Depends(get_db),
    api_key: str = Depends(api_key_header),
    api_key_name: str = Depends(api_key_name_header)
) -> ServiceAccount:
    """
    Validate API key authentication for service accounts.
    This is used for non-user entities like Airflow to access the API.
    """
    if not api_key or not api_key_name:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key and API key name are required",
            headers={"WWW-Authenticate": "APIKey"},
        )
    
    service_account = crud.service_account.verify_api_key(db, api_key_name, api_key)
    
    if not service_account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key or API key name",
            headers={"WWW-Authenticate": "APIKey"},
        )
    
    return service_account

async def get_service_account_from_bearer(
    db: Session = Depends(get_db),
    authorization: str = Header(None)
) -> ServiceAccount:
    """
    Validate API key authentication for service accounts from Authorization header.
    This allows service accounts to authenticate with Bearer token.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Expected format: "Bearer API_KEY"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key = parts[1]
    service_account = crud.service_account.find_by_api_key(db, api_key)
    
    if not service_account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return service_account

async def get_current_user_or_service_account(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(api_key_header),
    api_key_name: Optional[str] = Depends(api_key_name_header),
    authorization: Optional[str] = Header(None)
) -> Union[User, ServiceAccount]:
    """
    Try to authenticate with either user token or service account API key.
    This allows endpoints to be accessed by both humans and services.
    Supports both X-API-Key header and Bearer token for service accounts.
    """
    # First try token auth - this is likely the most common path
    if token:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            token_data = schemas.TokenPayload(**payload)
            
            user = crud.user.get(db, id=token_data.sub)
            if user and user.is_active:
                return user
        except (JWTError, ValidationError):
            # Don't raise yet, try other auth methods
            pass
    
    # Then try API key auth with headers
    if api_key and api_key_name:
        service_account = crud.service_account.verify_api_key(db, api_key_name, api_key)
        if service_account:
            return service_account
    
    # Finally try Bearer auth for service accounts (only if not already tried as token auth)
    if authorization and authorization.lower().startswith("bearer "):
        parts = authorization.split()
        if len(parts) == 2:
            api_key = parts[1]
            service_account = crud.service_account.find_by_api_key(db, api_key)
            if service_account:
                return service_account
    
    # If we got here, all auth methods failed
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    ) 