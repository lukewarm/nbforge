from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
import secrets
import string

from app import crud
from app.api import deps
from app.models.user import User
from app.schemas.service_account import (
    ServiceAccountCreate,
    ServiceAccountResponse,
    ServiceAccountWithKey,
    ServiceAccountUpdate,
    ServiceAccountKeyReset
)

router = APIRouter()


def generate_api_key(length: int = 40) -> str:
    """Generate a secure random API key"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


@router.post("/service-accounts", response_model=ServiceAccountWithKey)
async def create_service_account(
    *, 
    db: Session = Depends(deps.get_db),
    service_account_in: ServiceAccountCreate,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Create a new service account with generated API key.
    Only superusers can create service accounts.
    """
    # Check if service account with this name already exists
    service_account = crud.service_account.get_by_name(db, name=service_account_in.name)
    if service_account:
        raise HTTPException(
            status_code=400,
            detail=f"Service account with name '{service_account_in.name}' already exists"
        )
    
    # Generate a random API key
    api_key = generate_api_key()
    
    # Create the service account
    service_account = crud.service_account.create(
        db=db,
        name=service_account_in.name,
        description=service_account_in.description,
        raw_api_key=api_key
    )
    
    # Return the service account with the API key (only time it's returned)
    return {
        **ServiceAccountResponse.model_validate(service_account).model_dump(),
        "api_key": api_key
    }


@router.get("/service-accounts", response_model=List[ServiceAccountResponse])
async def get_service_accounts(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    List all service accounts.
    Only superusers can list service accounts.
    """
    service_accounts = crud.service_account.get_all(db, skip=skip, limit=limit)
    return service_accounts


@router.get("/service-accounts/{service_account_id}", response_model=ServiceAccountResponse)
async def get_service_account(
    *,
    db: Session = Depends(deps.get_db),
    service_account_id: str,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Get a specific service account.
    Only superusers can get service account details.
    """
    service_account = crud.service_account.get(db, id=service_account_id)
    if not service_account:
        raise HTTPException(status_code=404, detail="Service account not found")
    return service_account


@router.put("/service-accounts/{service_account_id}", response_model=ServiceAccountResponse)
async def update_service_account(
    *,
    db: Session = Depends(deps.get_db),
    service_account_id: str,
    service_account_in: ServiceAccountUpdate,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Update a service account.
    Only superusers can update service accounts.
    """
    service_account = crud.service_account.get(db, id=service_account_id)
    if not service_account:
        raise HTTPException(status_code=404, detail="Service account not found")
    
    service_account = crud.service_account.update(
        db=db,
        service_account=service_account,
        name=service_account_in.name,
        description=service_account_in.description,
        is_active=service_account_in.is_active,
        permissions=service_account_in.permissions
    )
    return service_account


@router.post("/service-accounts/{service_account_id}/reset-key", response_model=ServiceAccountWithKey)
async def reset_service_account_key(
    *,
    db: Session = Depends(deps.get_db),
    service_account_id: str,
    _: ServiceAccountKeyReset = Body(...),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Reset a service account's API key.
    Only superusers can reset API keys.
    """
    service_account = crud.service_account.get(db, id=service_account_id)
    if not service_account:
        raise HTTPException(status_code=404, detail="Service account not found")
    
    # Generate a new API key
    new_api_key = generate_api_key()
    
    # Update the service account with the new key
    service_account = crud.service_account.update_api_key(
        db=db,
        service_account=service_account,
        new_raw_api_key=new_api_key
    )
    
    # Return the service account with the new API key
    return {
        **ServiceAccountResponse.model_validate(service_account).model_dump(),
        "api_key": new_api_key
    }


@router.delete("/service-accounts/{service_account_id}", response_model=dict)
async def delete_service_account(
    *,
    db: Session = Depends(deps.get_db),
    service_account_id: str,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Delete a service account.
    Only superusers can delete service accounts.
    """
    service_account = crud.service_account.get(db, id=service_account_id)
    if not service_account:
        raise HTTPException(status_code=404, detail="Service account not found")
    
    crud.service_account.delete(db, id=service_account_id)
    return {"message": "Service account successfully deleted"} 