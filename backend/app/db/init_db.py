import logging
from sqlalchemy.orm import Session
from app.core.config import get_settings

from app.db.base_class import Base
from app.db.session import engine

# Make sure all SQLAlchemy models are imported before initializing DB
# otherwise, SQLAlchemy might fail to initialize relationships properly
from app.models import User

logger = logging.getLogger(__name__)
settings = get_settings()

def init_db(db: Session) -> None:
    """Initialize database tables and check for admin users"""
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

    # # Check if there are any admin users
    # admin_users = db.query(User).filter(User.is_superuser == True).all()
    
    # if not admin_users:
    #     logger.info("No admin users found. Checking for non-demo users...")
    #     # Get all users that are not demo users
    #     non_demo_users = db.query(User).filter(User.email.notin_([settings.DEMO_USER])).all()
        
    #     if non_demo_users:
    #         # Make the first non-demo user an admin
    #         first_user = non_demo_users[0]
    #         logger.info(f"Making first non-demo user ({first_user.email}) an admin")
    #         first_user.is_superuser = True
    #         db.add(first_user)
    #         db.commit()
    #     else:
    #         logger.info("No non-demo users found. Please create an admin user using the create_superuser.py script") 