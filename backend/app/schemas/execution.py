from pydantic import BaseModel, Field, validator
from typing import Dict, Optional, Literal, List, Any
from datetime import datetime

# The status flow:
# 1. pending (initial db creation)
# 2. submitted (after k8s job is created but not yet running)
# 3. running (notebook runner started execution)
# 4. completed/failed (final states)
# 5. cancelled (manual cancellation)
ExecutionStatusType = Literal['pending', 'running', 'completed', 'failed', 'cancelled', 'submitted']

class ExecutionCreate(BaseModel):
    notebook_path: str = Field(..., min_length=1)
    parameters: Dict = Field(default_factory=dict)
    python_version: Optional[str] = None
    cpu_milli: Optional[int] = None
    memory_mib: Optional[int] = None
    force_rerun: Optional[bool] = Field(default=None, description="Force rerun even if duplicate exists")

    @validator('notebook_path')
    def validate_notebook_path(cls, v):
        if not v.endswith('.ipynb'):
            raise ValueError('notebook_path must end with .ipynb')
        return v

class DuplicateExecutionResponse(BaseModel):
    """Response when a potential duplicate execution is found"""
    is_duplicate: bool = Field(..., description="Whether a duplicate execution was found")
    message: str = Field(..., description="Message about the duplicate")
    original_execution: Optional["ExecutionResponse"] = Field(None, description="The original execution that this would duplicate")
    
class ExecutionCreateResponse(BaseModel):
    """Response for creating a new execution"""
    execution: "ExecutionResponse"
    is_duplicate: bool = Field(default=False, description="Whether this is a duplicate of an existing execution")

class ExecutionUpdate(BaseModel):
    """Schema for updating an execution"""
    notebook_path: Optional[str] = None
    parameters: Optional[Dict] = None
    status: Optional[ExecutionStatusType] = None
    python_version: Optional[str] = None
    cpu_milli: Optional[int] = None
    memory_mib: Optional[int] = None

class ExecutionStatusUpdate(BaseModel):
    """Schema for updating execution status"""
    status: ExecutionStatusType
    error: Optional[str] = None
    output_notebook: Optional[str] = None
    output_html: Optional[str] = None
    outputs: Optional[Dict[str, Any]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if v and values.get('start_time') and v < values['start_time']:
            raise ValueError('end_time cannot be before start_time')
        return v

class UserInfo(BaseModel):
    id: str
    username: str
    email: str
    
    class Config:
        orm_mode = True
        from_attributes = True

class ServiceAccountInfo(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True

class ExecutionResponse(BaseModel):
    id: str
    notebook_path: str
    notebook_name: Optional[str] = None  # Human-readable notebook name
    parameters: Dict
    status: ExecutionStatusType
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    output_notebook: Optional[str] = None
    output_html: Optional[str] = None
    python_version: str
    cpu_milli: int
    memory_mib: int
    user: Optional[UserInfo] = None
    service_account: Optional[ServiceAccountInfo] = None
    notebook_hash: Optional[str] = None
    parameters_hash: Optional[str] = None
    execution_hash: Optional[str] = None

    class Config:
        from_attributes = True 