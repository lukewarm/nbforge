from sqlalchemy import Column, String, DateTime, JSON, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime
import uuid

class Execution(Base):
    __tablename__ = "executions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    notebook_path = Column(String, index=True)
    parameters = Column(JSON)
    status = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error = Column(String, nullable=True)
    output_notebook = Column(String, nullable=True)
    output_html = Column(String, nullable=True)
    python_version = Column(String)
    cpu_milli = Column(Integer)
    memory_mib = Column(Integer)
    requirements = Column(JSON, nullable=True, default=[])
    outputs = Column(JSON, nullable=True)
    # New fields for duplicate detection
    notebook_hash = Column(String, nullable=True, index=True)
    parameters_hash = Column(String, nullable=True, index=True)
    execution_hash = Column(String, nullable=True, index=True)  # Combined hash for both notebook and parameters
    callback_token = Column(String, nullable=True, index=True)
    
    # Add relationship to user if you have authentication
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="executions")
    
    # Add relationship to service account for API executions
    service_account_id = Column(String, ForeignKey("service_accounts.id"), nullable=True)
    service_account = relationship("ServiceAccount", back_populates="executions")
    
    # Transient attribute (not stored in DB) for the human-readable notebook name
    notebook_name = None
