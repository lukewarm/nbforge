from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Header, Query
from typing import Dict, Optional, List, Any, Union
from pydantic import BaseModel
from app.core.config import get_settings
import logging
from sqlalchemy.orm import Session
from datetime import datetime
from app.services.execution_service import ExecutionService
from app.db.session import get_db
from app.schemas.execution import (
    ExecutionCreate,
    ExecutionResponse,
    ExecutionStatusUpdate,
    ExecutionCreateResponse,
    DuplicateExecutionResponse
)
from app.models.execution import Execution
from uuid import UUID
from app.crud import execution as crud
from app.models.user import User
from app.models.service_account import ServiceAccount
from app.api import deps
from fastapi import status

logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()

def get_execution_service(db: Session = Depends(get_db)) -> ExecutionService:
    """Dependency to get execution service"""
    return ExecutionService(db)

@router.post("/executions/check-duplicate", response_model=DuplicateExecutionResponse, 
             summary="Check for duplicate executions",
             description="Check if a notebook execution with the same notebook and parameters already exists.")
async def check_duplicate_execution(
    execution: ExecutionCreate,
    service: ExecutionService = Depends(get_execution_service),
    current_principal: Union[User, ServiceAccount] = Depends(deps.get_current_user_or_service_account)
):
    """Check for duplicate executions"""
    # Check if this is a service account or a user
    user_id = None
    if isinstance(current_principal, User):
        user_id = current_principal.id
        
    try:
        # Check for duplicates
        is_duplicate, duplicate = await service.check_for_duplicate_execution(
            notebook_path=execution.notebook_path,
            parameters=execution.parameters,
            user_id=user_id if user_id else None
        )
        
        if is_duplicate and duplicate:
            return {
                "is_duplicate": True,
                "message": f"Found a duplicate execution from {duplicate.created_at.isoformat()}",
                "original_execution": duplicate
            }
        else:
            return {
                "is_duplicate": False,
                "message": "No duplicate executions found",
                "original_execution": None
            }
    except Exception as e:
        logger.error(f"Failed to check for duplicate executions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/executions", response_model=ExecutionCreateResponse, 
             summary="Create a new notebook execution",
             description="Execute a notebook with the specified parameters using the notebook runner")
async def create_execution(
    execution: ExecutionCreate,
    check_duplicate: bool = Query(True, description="Whether to check for duplicates before creating the execution"),
    service: ExecutionService = Depends(get_execution_service),
    current_principal: Union[User, ServiceAccount] = Depends(deps.get_current_user_or_service_account)
):
    """Create a new notebook execution"""
    # Check if this is a service account or a user
    user_id = None
    service_account_id = None
    # Whether to force rerun and skip duplicate checks
    api_execution = False
    
    if isinstance(current_principal, User):
        user_id = current_principal.id
    elif isinstance(current_principal, ServiceAccount):
        # For service accounts, check permission
        if not current_principal.permissions.get("create_execution", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This service account does not have permission to create executions"
            )
        service_account_id = current_principal.id
        # Mark as API execution for force_rerun logic below
        api_execution = True
    
    # Log the force_rerun and check_duplicate flags
    logger.info(f"Execution request - force_rerun: {execution.force_rerun}, check_duplicate: {check_duplicate}")
    
    # For API executions, always force rerun unless explicitly set to False
    if api_execution and execution.force_rerun is None:
        force_rerun = True
    else:
        force_rerun = execution.force_rerun or not check_duplicate
    
    logger.info(f"Effective force_rerun flag: {force_rerun}")
    
    try:
        # Create a new execution with duplicate detection if requested
        execution_obj, is_duplicate = await service.create_execution(
            notebook_path=execution.notebook_path,
            parameters=execution.parameters,
            python_version=execution.python_version,
            cpu_milli=execution.cpu_milli,
            memory_mib=execution.memory_mib,
            user_id=user_id,
            service_account_id=service_account_id,
            force_rerun=force_rerun
        )
        
        # Explicitly construct a valid ExecutionCreateResponse object
        # This ensures we follow the schema exactly
        response = ExecutionCreateResponse(
            execution=execution_obj,
            is_duplicate=is_duplicate
        )
        return response
    except Exception as e:
        logger.error(f"Failed to create execution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executions", response_model=List[ExecutionResponse])
async def list_executions(
    skip: int = 0, 
    limit: int = 100,
    notebook_path: Optional[str] = None,
    service: ExecutionService = Depends(get_execution_service),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Retrieve executions with notebook metadata.
    
    This endpoint returns executions enriched with notebook names.
    """
    try:
        # Use the service to get executions with notebook metadata
        executions = await service.list_executions(notebook_path)
        
        # Apply skip and limit after all metadata is added
        return executions[skip:skip+limit]
    except Exception as e:
        logger.error(f"Failed to list executions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    service: ExecutionService = Depends(get_execution_service),
    current_principal: Union[User, ServiceAccount] = Depends(deps.get_current_user_or_service_account)
):
    """Get details of a specific execution"""
    try:
        execution = await service.get_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        return execution
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get execution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/executions/{execution_id}/status")
async def update_execution_status(
    execution_id: str,
    status_update: ExecutionStatusUpdate,
    service: ExecutionService = Depends(get_execution_service),
    callback_token: str = Header(..., alias="X-Callback-Token")
):
    """Update execution status (called by notebook runner)"""
    try:
        # Validate the callback token
        token_valid = await service.validate_callback_token(execution_id, callback_token)
        if not token_valid:
            raise HTTPException(status_code=401, detail="Invalid callback token")
            
        # Update execution status
        execution = await service.update_execution_status(
            execution_id=execution_id,
            status=status_update.status,
            error=status_update.error,
            output_notebook=status_update.output_notebook,
            output_html=status_update.output_html,
            start_time=status_update.start_time,
            end_time=status_update.end_time,
            outputs=status_update.outputs
        )
        
        return {"status": "updated", "execution_id": execution_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update execution status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/executions/{execution_id}/cancel")
async def cancel_execution(
    execution_id: str,
    service: ExecutionService = Depends(get_execution_service),
    current_user: User = Depends(deps.get_current_user)
):
    """Cancel a running execution"""
    try:
        # Get the execution first
        execution = await service.get_execution(execution_id)
        
        # Check if user is authorized to cancel this execution
        # User can cancel if they are the owner or if they are an admin
        if execution.user_id != current_user.id and not current_user.is_superuser:
            logger.warning(f"User {current_user.id} attempted to cancel execution {execution_id} owned by {execution.user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to cancel this execution"
            )
            
        # Check if execution can be canceled based on its status
        if execution.status in ["completed", "failed", "cancelled"]:
            status_message = f"Cannot cancel execution in '{execution.status}' state"
            logger.warning(f"{status_message}: {execution_id}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=status_message
            )
        
        # Proceed with cancellation
        result = await service.cancel_execution(execution_id)
        
        # Check if cancellation was successful
        if result["success"]:
            return {"status": "cancelled", "execution_id": execution_id, "message": result["reason"]}
        else:
            # If the execution status has changed to a terminal state since we checked
            if result["status"] in ["completed", "failed", "cancelled"]:
                logger.warning(f"Execution {execution_id} state changed to {result['status']} during cancellation attempt")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=result["reason"]
                )
            
            # Handle cases where the job wasn't found in Kubernetes
            if "not found" in result["reason"].lower() or "doesn't exist" in result["reason"].lower():
                logger.warning(f"Job for execution {execution_id} not found: {result['reason']}")
                
                # Since the job wasn't found in Kubernetes, we should update the database
                # to reflect the current state
                try:
                    await service.update_execution_status_if_not_found(execution_id)
                    status_message = f"Job for execution {execution_id} not found in Kubernetes. It may have already completed, failed, or been terminated."
                except Exception as db_err:
                    logger.error(f"Failed to update execution status: {str(db_err)}")
                    status_message = f"Failed to cancel execution: {execution_id}. The job might not exist anymore."
                    
                # Return a 404 error since the job doesn't exist
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=status_message
                )
            else:
                # Any other cancellation failure
                logger.error(f"Failed to cancel execution {execution_id}: {result['reason']}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["reason"]
                )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Failed to cancel execution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executions/{execution_id}/logs")
async def get_execution_logs(
    execution_id: str,
    service: ExecutionService = Depends(get_execution_service),
    current_principal: Union[User, ServiceAccount] = Depends(deps.get_current_user_or_service_account)
):
    """Get logs for a specific execution"""
    try:
        # This would need to be implemented in the ExecutionService
        # to fetch logs from Kubernetes
        raise HTTPException(status_code=501, detail="Not implemented")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get execution logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executions/{execution_id}/output")
async def get_execution_output(
    execution_id: str,
    format: str = "html",
    service: ExecutionService = Depends(get_execution_service),
    current_principal: Union[User, ServiceAccount] = Depends(deps.get_current_user_or_service_account)
):
    """Get the output of a completed execution in the specified format"""
    try:
        execution = await service.get_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
            
        if execution.status != "completed":
            raise HTTPException(status_code=400, detail="Execution not completed")
            
        if format == "html" and execution.output_html:
            # Return HTML output
            # This would need to be implemented to fetch the HTML from storage
            raise HTTPException(status_code=501, detail="HTML output retrieval not implemented")
        elif format == "notebook" and execution.output_notebook:
            # Return notebook output
            # This would need to be implemented to fetch the notebook from storage
            raise HTTPException(status_code=501, detail="Notebook output retrieval not implemented")
        else:
            raise HTTPException(status_code=400, detail=f"Output format {format} not available")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get execution output: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
