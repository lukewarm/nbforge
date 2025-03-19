from sqlalchemy import Column, String, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime
import uuid

class ServiceAccount(Base):
    """Service account for API access by external systems"""
    __tablename__ = "service_accounts"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True, unique=True)
    description = Column(String, nullable=True)
    api_key_hash = Column(String)  # Hashed API key, never store raw
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    permissions = Column(JSON, default={"create_execution": True})  # Permissions as JSON 
    
    # Relationship to executions created by this service account
    executions = relationship("Execution", back_populates="service_account") 