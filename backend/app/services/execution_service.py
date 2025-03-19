from typing import Dict, Optional, List, Any, Tuple
from datetime import datetime
import uuid
import json
import logging
from app.models.execution import Execution
from app.services.batch_executors.k8s_executor import K8sExecutor
from app.core.config import get_settings
from sqlalchemy.orm import Session
from app.services.notebook_metadata import NotebookMetadataExtractor
from app.services.storage.factory import create_storage_service
from app.services.email.email import email_service
from app.models.user import User
from app.core.security import create_callback_token
from app.utils.hash_utils import get_notebook_hash, get_parameters_hash, get_execution_hash

settings = get_settings()
logger = logging.getLogger(__name__)

class ExecutionService:
    def __init__(self, db: Session):
        self.db = db
        self.batch_executor = K8sExecutor()
        self.storage = create_storage_service()
        # Initialize a cache for notebook metadata
        self.notebook_metadata_cache = {}

    async def _convert_parameters_using_metadata(self, notebook_content: bytes, parameters: Dict) -> Dict:
        """
        Convert parameter values based on their declared types in the notebook.
        
        Args:
            notebook_content: Raw notebook content
            parameters: Dictionary of parameter values to convert
            
        Returns:
            Dictionary of parameters with values converted to appropriate types
        """
        if not parameters:
            return {}
            
        # Extract parameter definitions from notebook
        metadata_extractor = NotebookMetadataExtractor(notebook_content.decode('utf-8'))
        metadata = metadata_extractor.extract_metadata()
        param_definitions = metadata.get('parameters', [])
        
        # Create a mapping of parameter names to their types
        param_types = {param['name']: param['type'] for param in param_definitions if 'name' in param and 'type' in param}
        
        if not param_types:
            logger.warning("No parameter definitions found in notebook metadata")
            return parameters
            
        logger.info(f"Found parameter definitions: {param_types}")
        
        # Convert parameters based on their types
        converted_params = {}
        for name, value in parameters.items():
            # Skip None values
            if value is None:
                converted_params[name] = None
                continue
                
            # Get the declared type for this parameter
            param_type = param_types.get(name)
            if not param_type:
                logger.warning(f"No type definition found for parameter '{name}', leaving as-is")
                converted_params[name] = value
                continue
                
            try:
                # Convert value based on declared type
                if param_type.lower() in ('int', 'integer'):
                    if isinstance(value, str):
                        converted_params[name] = int(value)
                    else:
                        converted_params[name] = int(value) if isinstance(value, (int, float)) else value
                        
                elif param_type.lower() in ('float', 'double', 'number'):
                    if isinstance(value, str):
                        converted_params[name] = float(value)
                    else:
                        converted_params[name] = float(value) if isinstance(value, (int, float)) else value
                        
                elif param_type.lower() in ('bool', 'boolean'):
                    if isinstance(value, str):
                        if value.lower() == 'true':
                            converted_params[name] = True
                        elif value.lower() == 'false':
                            converted_params[name] = False
                        else:
                            converted_params[name] = bool(value)
                    else:
                        converted_params[name] = bool(value)
                        
                elif param_type.lower().startswith(('list', 'array')):
                    # Handle list type
                    if isinstance(value, str):
                        # Try to parse as JSON if it's a string
                        try:
                            parsed_value = json.loads(value.replace("'", '"'))
                            converted_params[name] = parsed_value if isinstance(parsed_value, list) else [value]
                        except json.JSONDecodeError:
                            # If not valid JSON, split by comma if it looks like a comma-separated list
                            if ',' in value:
                                converted_params[name] = [item.strip() for item in value.split(',')]
                            else:
                                converted_params[name] = [value]
                    elif isinstance(value, list):
                        converted_params[name] = value
                    else:
                        converted_params[name] = [value]
                        
                elif param_type.lower().startswith(('dict', 'object', 'map')):
                    # Handle dictionary type
                    if isinstance(value, str):
                        try:
                            converted_params[name] = json.loads(value.replace("'", '"'))
                        except json.JSONDecodeError:
                            converted_params[name] = value
                    else:
                        converted_params[name] = value
                        
                else:
                    # For other types (string, etc.), keep as is
                    converted_params[name] = value
                    
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to convert parameter '{name}' to {param_type}: {e}")
                # Keep original value if conversion fails
                converted_params[name] = value
                
        return converted_params

    async def check_for_duplicate_execution(
        self,
        notebook_path: str,
        parameters: Dict,
        user_id: Optional[str] = None
    ) -> Tuple[bool, Optional[Execution]]:
        """
        Check if a notebook execution with the same notebook and parameters already exists.
        
        Args:
            notebook_path: Path to the notebook
            parameters: Execution parameters
            user_id: Optional user ID to restrict search to user's executions
            
        Returns:
            Tuple of (duplicate_exists, duplicate_execution)
        """
        # Download and hash the notebook
        notebook_content = await self.storage.download_notebook(notebook_path)
        notebook_hash = get_notebook_hash(notebook_content)
        parameters_hash = get_parameters_hash(parameters)
        execution_hash = get_execution_hash(notebook_hash, parameters_hash)
        
        # Query for potential duplicates
        # Only consider executions that were successfully completed (no errors)
        query = self.db.query(Execution).filter(
            Execution.execution_hash == execution_hash,
            Execution.status == "completed",
            Execution.error.is_(None)  # Only consider executions with no errors
        )
        
        # Optionally filter by user_id
        if user_id:
            query = query.filter(Execution.user_id == user_id)
        
        # Get the most recent potential duplicate
        duplicate = query.order_by(Execution.created_at.desc()).first()
        
        return (duplicate is not None, duplicate)

    async def create_execution(
        self,
        notebook_path: str,
        parameters: Dict,
        python_version: Optional[str] = None,
        cpu_milli: Optional[int] = None,
        memory_mib: Optional[int] = None,
        user_id: Optional[str] = None,
        service_account_id: Optional[str] = None,
        force_rerun: bool = False
    ) -> Tuple[Execution, bool]:
        """
        Create a new notebook execution, with optional duplicate detection.
        
        Status workflow:
        - Initially set to 'pending' when execution is created in the database
        - Set to 'submitted' after the K8s job is successfully created
        - The notebook runner will update to 'running' when it starts
        - Finally updated to 'completed' or 'failed' by the notebook runner
        - Can be manually set to 'cancelled' via the cancel_execution method
        
        Args:
            notebook_path: Path to the notebook
            parameters: Execution parameters
            python_version: Python version to use
            cpu_milli: CPU milli to allocate
            memory_mib: Memory MiB to allocate
            user_id: User ID
            service_account_id: Service account ID for API executions
            force_rerun: Whether to force rerun even if duplicate exists
            
        Returns:
            Tuple of (execution, is_duplicate)
        """
        # Fetch notebook content
        notebook_content = await self.storage.download_notebook(notebook_path)
        
        # Extract notebook metadata to get the human-readable name
        metadata_extractor = NotebookMetadataExtractor(notebook_content.decode('utf-8'))
        metadata = metadata_extractor.extract_metadata()
        
        # Add notebook name to cache
        notebook_name = metadata["identity"].get('name', '')
        self.notebook_metadata_cache[notebook_path] = notebook_name
        
        # Convert parameters using notebook metadata
        converted_parameters = await self._convert_parameters_using_metadata(notebook_content, parameters)
        logger.info(f"Converted parameters: {converted_parameters}")
        
        # Log force_rerun status
        logger.info(f"Force rerun flag: {force_rerun}")
        
        # Check for duplicates unless force_rerun is specified
        is_duplicate = False
        if not force_rerun:
            logger.info("Checking for duplicate executions")
            is_duplicate, duplicate = await self.check_for_duplicate_execution(
                notebook_path, converted_parameters, user_id=None  # Check for duplicates globally
            )
            if is_duplicate:
                logger.info(f"Found duplicate execution: {duplicate.id}")
                # Add notebook_name to the duplicate execution object
                duplicate.notebook_name = metadata["identity"].get('name', '')
                return duplicate, True
        else:
            logger.info("Skipping duplicate check because force_rerun=True")
        
        # Compute hashes for the execution
        notebook_hash = get_notebook_hash(notebook_content)
        parameters_hash = get_parameters_hash(converted_parameters)
        execution_hash = get_execution_hash(notebook_hash, parameters_hash)
        
        # Use metadata for resources if not explicitly provided
        resources = metadata.get('resources', {})
        if not python_version:
            python_version = settings.DEFAULT_PYTHON_VERSION
        
        if not cpu_milli and resources.get('cpu_milli'):
            cpu_milli = resources['cpu_milli']
        elif not cpu_milli:
            cpu_milli = settings.DEFAULT_CPU_MILLI
        
        if not memory_mib and resources.get('memory_mib'):
            memory_mib = resources['memory_mib']
        elif not memory_mib:
            memory_mib = settings.DEFAULT_MEMORY_MIB
        
        # Extract requirements
        requirements = metadata.get('requirements', [])
        
        # Generate a unique job ID and callback token
        job_id = str(uuid.uuid4())
        callback_token = create_callback_token()
        
        # Create execution record with converted parameters
        execution = Execution(
            id=job_id,
            notebook_path=notebook_path,
            parameters=converted_parameters,
            status="pending",
            created_at=datetime.utcnow(),
            python_version=python_version,
            cpu_milli=cpu_milli,
            memory_mib=memory_mib,
            requirements=requirements,
            callback_token=callback_token,
            user_id=user_id,
            service_account_id=service_account_id,
            notebook_hash=notebook_hash,
            parameters_hash=parameters_hash,
            execution_hash=execution_hash
        )
        
        self.db.add(execution)
        self.db.commit()
        
        try:
            # Create the job with converted parameters
            await self.batch_executor.create_job(
                notebook_path=notebook_path,
                parameters=converted_parameters,
                python_version=python_version,
                job_name=job_id,
                cpu_milli=cpu_milli,
                memory_mib=memory_mib,
                requirements=requirements,
                callback_token=callback_token
            )
            
            # Update status to submitted
            execution.status = "submitted"
            self.db.commit()
            
        except Exception as e:
            # Update status to failed if job creation fails
            execution.status = "failed"
            execution.error = str(e)
            self.db.commit()
            raise
        
        # Add notebook_name to the execution object before returning
        execution.notebook_name = notebook_name
        
        return execution, False

    async def get_execution(self, execution_id: str) -> Execution:
        """Get a specific execution by ID and enrich with notebook metadata"""
        execution = self.db.query(Execution).get(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
            
        # Add notebook name if available
        if execution.notebook_path:
            # Check cache first
            if execution.notebook_path in self.notebook_metadata_cache:
                execution.notebook_name = self.notebook_metadata_cache[execution.notebook_path]
            else:
                try:
                    # If not in cache, fetch and cache it
                    notebook_content = await self.storage.download_notebook(execution.notebook_path)
                    metadata_extractor = NotebookMetadataExtractor(notebook_content.decode('utf-8'))
                    metadata = metadata_extractor.extract_metadata()
                    
                    notebook_name = metadata["identity"].get('name', '')
                    execution.notebook_name = notebook_name
                    
                    # Add to cache
                    self.notebook_metadata_cache[execution.notebook_path] = notebook_name
                except Exception as e:
                    # Log error but don't fail the request
                    logger.warning(f"Failed to get notebook metadata for path {execution.notebook_path}: {str(e)}")
                    execution.notebook_name = ""
        
        return execution
    
    async def list_executions(self, notebook_path: Optional[str] = None) -> list:
        """List executions, optionally filtered by notebook path, and enrich with notebook metadata"""
        query = self.db.query(Execution)
        if notebook_path:
            query = query.filter(Execution.notebook_path == notebook_path)
        
        executions = query.order_by(Execution.created_at.desc()).all()
        
        # Fetch notebook metadata for all executions to get their names
        # Group by notebook_path to avoid redundant fetches
        notebook_names = {}
        for execution in executions:
            if execution.notebook_path:
                # Check if we have this path in the cache
                if execution.notebook_path in self.notebook_metadata_cache:
                    notebook_names[execution.notebook_path] = self.notebook_metadata_cache[execution.notebook_path]
                # Only fetch metadata if we haven't seen this notebook before
                elif execution.notebook_path not in notebook_names:
                    try:
                        # Download notebook content
                        notebook_content = await self.storage.download_notebook(execution.notebook_path)
                        
                        # Extract metadata to get the name
                        metadata_extractor = NotebookMetadataExtractor(notebook_content.decode('utf-8'))
                        metadata = metadata_extractor.extract_metadata()
                        
                        # Store the name for this path
                        notebook_name = metadata["identity"].get('name', '')
                        notebook_names[execution.notebook_path] = notebook_name
                        
                        # Add to the cache
                        self.notebook_metadata_cache[execution.notebook_path] = notebook_name
                    except Exception as e:
                        # Log the error but don't fail the request
                        logger.warning(f"Failed to get notebook metadata for path {execution.notebook_path}: {str(e)}")
                        notebook_names[execution.notebook_path] = ""
                
                # Set the notebook name as a transient attribute
                execution.notebook_name = notebook_names.get(execution.notebook_path, "")
        
        return executions
    
    async def update_execution_status(
        self,
        execution_id: str,
        status: str,
        error: Optional[str] = None,
        output_notebook: Optional[str] = None,
        output_html: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        outputs: Optional[Dict] = None
    ) -> Execution:
        """Update execution status"""
        execution = self.db.query(Execution).get(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
            
        execution.status = status
        if start_time:
            execution.started_at = start_time
        if end_time:
            execution.completed_at = end_time
        if error:
            execution.error = error
        if output_notebook:
            execution.output_notebook = output_notebook
        if output_html:
            execution.output_html = output_html
        if outputs:
            execution.outputs = outputs
            
        # Send email notification if execution is completed or failed
        # Only send notifications for user-triggered executions (not API/service account executions)
        if status in ["completed", "failed"] and execution.user_id and not execution.service_account_id:
            user = self.db.query(User).filter(User.id == execution.user_id).first()
            if user and user.email:
                await email_service.send_execution_notification(
                    email_to=user.email,
                    execution_id=execution_id,
                    notebook_path=execution.notebook_path,
                    status=status,
                    error=error,
                    output_html=execution.output_html,
                    output_notebook=execution.output_notebook
                )
            
        self.db.commit()
        return execution

    async def cancel_execution(self, execution_id: str) -> dict:
        """
        Cancel a running execution
        
        Returns a dictionary with:
        - success: bool - Whether the cancellation was successful
        - reason: str - Explanation for why cancellation succeeded or failed
        - status: str - The current status of the execution
        """
        execution = self.db.query(Execution).get(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
            
        if execution.status in ["completed", "failed", "cancelled"]:
            reason = f"Cannot cancel execution {execution_id} as it is already in {execution.status} state"
            logger.info(reason)
            return {
                "success": False,
                "reason": reason,
                "status": execution.status
            }
        
        try:
            # For K8s executor, we need to prepend the job name prefix
            job_name = f"notebook-execution-{execution_id}"
            logger.info(f"Attempting to cancel job {job_name} for execution {execution_id}")
            
            success = await self.batch_executor.cancel_job(job_name)
            
            if success:
                logger.info(f"Successfully cancelled execution {execution_id}")
                execution.status = "cancelled"
                execution.completed_at = datetime.utcnow()
                self.db.commit()
                return {
                    "success": True,
                    "reason": "Execution successfully cancelled",
                    "status": "cancelled"
                }
            else:
                # Get the current status of the execution
                # It's possible the execution completed while we were trying to cancel it
                execution = self.db.query(Execution).get(execution_id)
                current_status = execution.status
                
                # If the execution is now in a terminal state, the job likely completed before we could cancel it
                if current_status in ["completed", "failed", "cancelled"]:
                    reason = f"Cannot cancel execution that has already {current_status}"
                    logger.info(reason)
                    return {
                        "success": False,
                        "reason": reason,
                        "status": current_status
                    }
                
                # Otherwise, there was some other issue with cancellation
                reason = f"Failed to cancel execution {execution_id} - batch executor returned False"
                logger.error(reason)
                return {
                    "success": False,
                    "reason": reason,
                    "status": current_status
                }
        except Exception as e:
            error_msg = f"Error occurred while cancelling execution {execution_id}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "reason": error_msg,
                "status": execution.status
            }

    async def update_execution_status_if_not_found(self, execution_id: str) -> None:
        """
        Update execution status when the job is not found in Kubernetes.
        This happens when the job has already completed, failed, or been deleted outside of our system.
        """
        execution = self.db.query(Execution).get(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
            
        # Only update the status if it's still in a state that suggests it's running
        if execution.status in ["pending", "running", "submitted"]:
            # Set status to 'failed' with an appropriate message
            logger.info(f"Updating execution {execution_id} status to 'failed' as the job was not found in Kubernetes")
            execution.status = "failed"
            execution.error = "Job not found in Kubernetes. It may have been terminated outside of the system."
            execution.completed_at = datetime.utcnow()
            self.db.commit()
            
        return execution

    async def validate_callback_token(self, execution_id: str, token: str) -> bool:
        """Validate that the provided token matches the execution's callback token"""
        execution = self.db.query(Execution).get(execution_id)
        if not execution:
            return False
        
        return execution.callback_token == token 