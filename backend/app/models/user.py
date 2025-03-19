from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from sqlalchemy.sql import func

from app.db.base_class import Base

# Many-to-many relationship between users and roles
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String, ForeignKey("users.id")),
    Column("role_id", String, ForeignKey("roles.id"))
)

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True)
    full_name = Column(String, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # OAuth related fields
    oauth_provider = Column(String, nullable=True)  # e.g., "google", "github"
    oauth_id = Column(String, nullable=True)        # ID from the provider
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    executions = relationship("Execution", back_populates="user")

class Role(Base):
    __tablename__ = "roles"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles") 