from typing import Optional, Dict
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ServiceAccountCreate(BaseModel):
    """Schema for creating a service account"""
    name: str = Field(..., description="Unique name for the service account")
    description: Optional[str] = Field(None, description="Optional description")


class ServiceAccountResponse(BaseModel):
    """Schema for service account response without sensitive data"""
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    last_used_at: Optional[datetime] = None
    is_active: bool
    permissions: Dict

    model_config = ConfigDict(from_attributes=True)


class ServiceAccountWithKey(ServiceAccountResponse):
    """Schema that includes the API key (only returned once during creation)"""
    api_key: str


class ServiceAccountUpdate(BaseModel):
    """Schema for updating a service account"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permissions: Optional[Dict] = None


class ServiceAccountKeyReset(BaseModel):
    """Schema for resetting an API key"""
    pass  # No fields needed, just triggers key reset 