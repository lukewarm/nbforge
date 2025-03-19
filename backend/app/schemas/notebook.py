from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

class NotebookExecution(BaseModel):
    job_id: str
    status: str
    notebook_path: str

class ExecutionStatus(BaseModel):
    job_id: str
    status: str
    error: Optional[str] = None

class NotebookResponse(BaseModel):
    path: str
    filename: str
    metadata: Dict[str, Any]
    content: Optional[str] = None
    
    class Config:
        from_attributes = True 