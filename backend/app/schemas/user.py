from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

class UserCreate(UserBase):
    password: str

class UserUpdateBase(BaseModel):
    """Base schema for user updates with all fields optional"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserUpdate(UserUpdateBase):
    password: Optional[str] = None
    current_password: Optional[str] = None  # For password verification
    new_password: Optional[str] = None      # For password changes

class UserInDBBase(UserBase):
    id: str
    created_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None

class UserPrivilegesUpdate(BaseModel):
    """Schema for updating user privileges"""
    is_superuser: bool = False
    is_active: bool = True 