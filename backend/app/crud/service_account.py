from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.service_account import ServiceAccount
from app.core.security import get_password_hash, verify_password


def create(db: Session, *, name: str, description: Optional[str], raw_api_key: str) -> ServiceAccount:
    """Create a new service account with a hashed API key"""
    api_key_hash = get_password_hash(raw_api_key)
    
    service_account = ServiceAccount(
        name=name,
        description=description,
        api_key_hash=api_key_hash,
        created_at=datetime.utcnow(),
        is_active=True,
        permissions={"create_execution": True}
    )
    
    db.add(service_account)
    db.commit()
    db.refresh(service_account)
    return service_account


def get(db: Session, id: str) -> Optional[ServiceAccount]:
    """Get a service account by ID"""
    return db.query(ServiceAccount).filter(ServiceAccount.id == id).first()


def get_by_name(db: Session, name: str) -> Optional[ServiceAccount]:
    """Get a service account by name"""
    return db.query(ServiceAccount).filter(ServiceAccount.name == name).first()


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[ServiceAccount]:
    """Get all service accounts"""
    return db.query(ServiceAccount).offset(skip).limit(limit).all()


def update(db: Session, *, service_account: ServiceAccount, 
           name: Optional[str] = None, 
           description: Optional[str] = None,
           is_active: Optional[bool] = None,
           permissions: Optional[dict] = None) -> ServiceAccount:
    """Update a service account"""
    if name is not None:
        service_account.name = name
    if description is not None:
        service_account.description = description
    if is_active is not None:
        service_account.is_active = is_active
    if permissions is not None:
        service_account.permissions = permissions
        
    db.add(service_account)
    db.commit()
    db.refresh(service_account)
    return service_account


def update_api_key(db: Session, *, service_account: ServiceAccount, new_raw_api_key: str) -> ServiceAccount:
    """Update a service account's API key"""
    service_account.api_key_hash = get_password_hash(new_raw_api_key)
    
    db.add(service_account)
    db.commit()
    db.refresh(service_account)
    return service_account


def update_last_used(db: Session, *, service_account: ServiceAccount) -> ServiceAccount:
    """Update when a service account was last used"""
    service_account.last_used_at = datetime.utcnow()
    
    db.add(service_account)
    db.commit()
    return service_account


def delete(db: Session, *, id: str) -> bool:
    """Delete a service account"""
    service_account = db.query(ServiceAccount).filter(ServiceAccount.id == id).first()
    if not service_account:
        return False
    
    db.delete(service_account)
    db.commit()
    return True


def verify_api_key(db: Session, name: str, api_key: str) -> Optional[ServiceAccount]:
    """Verify an API key for a service account and return the account if valid"""
    service_account = get_by_name(db, name)
    
    if not service_account:
        return None
        
    if not service_account.is_active:
        return None
        
    if not verify_password(api_key, service_account.api_key_hash):
        return None
        
    # Update last used time
    update_last_used(db, service_account=service_account)
    
    return service_account


def find_by_api_key(db: Session, api_key: str) -> Optional[ServiceAccount]:
    """Find a service account by its API key"""
    # Get active service accounts, but limit to a reasonable number to avoid overloading
    service_accounts = db.query(ServiceAccount).filter(ServiceAccount.is_active == True).limit(100).all()
    
    # Create a cache for this find operation to avoid repeatedly checking the same accounts
    checked_ids = set()
    
    # Check each one to find a matching API key
    for service_account in service_accounts:
        if service_account.id in checked_ids:
            continue
            
        checked_ids.add(service_account.id)
        if verify_password(api_key, service_account.api_key_hash):
            # Update last used time
            update_last_used(db, service_account=service_account)
            return service_account
    
    return None 