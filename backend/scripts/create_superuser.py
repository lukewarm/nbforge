#!/usr/bin/env python
"""
Script to create or elevate a superuser.
Usage: python -m backend.scripts.create_superuser <email>
"""

import sys
import logging
from dotenv import load_dotenv
from sqlalchemy.orm import Session

load_dotenv()

from app.db.session import SessionLocal
from app.core.config import get_settings
from app import crud
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()

def create_superuser(db: Session, email: str, password: str = None) -> None:
    """Create a superuser or elevate an existing user to superuser."""
    # Check if user exists
    user = crud.user.get_by_email(db, email=email)
    
    if user:
        # User exists, elevate to superuser
        logger.info(f"User {email} exists. Elevating to superuser...")
        user.is_superuser = True
        db.add(user)
        db.commit()
        logger.info(f"Successfully elevated {email} to superuser.")
    else:
        # User doesn't exist, create new superuser
        if not password:
            logger.error("Password is required to create a new user.")
            sys.exit(1)
            
        logger.info(f"Creating new superuser {email}...")
        user_in = {
            "email": email,
            "hashed_password": get_password_hash(password),
            "is_active": True,
            "is_superuser": True,
            "name": "Admin"
        }
        user = crud.user.create_with_fields(db, **user_in)
        logger.info(f"Successfully created superuser {email}.")

def main() -> None:
    """Main function to run from command line."""
    if len(sys.argv) < 2:
        logger.error("Email argument is required.")
        logger.info("Usage: python -m scripts.create_superuser <email> [password]")
        sys.exit(1)
        
    email = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) > 2 else None
    
    db = SessionLocal()
    try:
        create_superuser(db, email, password)
    finally:
        db.close()

if __name__ == "__main__":
    main() 