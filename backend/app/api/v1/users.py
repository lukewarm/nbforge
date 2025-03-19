from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import UserPrivilegesUpdate, UserUpdate, User as UserSchema
from app.crud.user import user
from app.models.user import User
from app.api import deps
from fastapi import status
from app.core.security import verify_password
import logging
import copy

logger = logging.getLogger(__name__)
router = APIRouter()

def redact_sensitive_data(data_dict):
    """Redact sensitive fields like passwords from logs"""
    if not isinstance(data_dict, dict):
        return data_dict
        
    redacted = copy.deepcopy(data_dict)
    sensitive_fields = ['password', 'current_password', 'new_password', 'hashed_password']
    
    for field in sensitive_fields:
        if field in redacted:
            redacted[field] = '********'
            
    return redacted

@router.patch("/users/{user_id}/privileges", response_model=UserSchema)
def update_user_privileges(
    user_id: str,
    privileges: UserPrivilegesUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """
    Update a user's privileges (superuser status).
    Only superusers can update privileges.
    """
    user_obj = user.get(db, id=user_id)
    if not user_obj:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    
    # Prevent superusers from removing their own superuser status
    if user_obj.id == current_user.id and not privileges.is_superuser:
        raise HTTPException(
            status_code=400,
            detail="Cannot remove your own superuser status",
        )
    
    # Update user privileges
    user_data = {
        "is_superuser": privileges.is_superuser,
        "is_active": privileges.is_active,
    }
    updated_user = user.update(db, db_obj=user_obj, obj_in=user_data)
    return updated_user

@router.patch("/users/me", response_model=UserSchema)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Update own user profile.
    """
    try:
        # Create a dictionary with only the fields to update
        update_data = user_update.dict(exclude_unset=True)
        
        # Log the data safely (without sensitive info)
        logger.info(f"Received profile update request from user: {current_user.email}")
        logger.debug(f"Update fields: {list(update_data.keys())}")
        
        # Check for username uniqueness if being updated
        if "username" in update_data and update_data["username"] != current_user.username:
            existing_user = user.get_by_username(db, username=update_data["username"])
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered",
                )
        
        # If the user is trying to change their email (though UI prevents this, API could be called directly)
        if "email" in update_data and update_data["email"] != current_user.email:
            existing_user = user.get_by_email(db, email=update_data["email"])
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )
        
        # If the user is trying to change their password
        if "new_password" in update_data:
            logger.info("Password change requested")
            
            # Require current password
            if "current_password" not in update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is required to set a new password",
                )
                
            # Verify current password
            current_password = update_data.pop("current_password")
            if not verify_password(current_password, current_user.hashed_password):
                logger.warning(f"Failed password change attempt for user: {current_user.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Current password is incorrect",
                )
                
            # Replace new_password with password for the UserUpdate schema
            update_data["password"] = update_data.pop("new_password")
            logger.info(f"Password updated for user: {current_user.email}")
        
        # Update the user
        updated_user = user.update(db, db_obj=current_user, obj_in=update_data)
        return updated_user
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise 

@router.get("/users", response_model=list[UserSchema])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """
    Retrieve all users. Only accessible to superusers.
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users 