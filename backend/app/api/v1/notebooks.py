from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, status, Response
from typing import List, Dict, Optional, Union
from pydantic import BaseModel
from app.services.storage.interface import BaseStorageService
from app.services.notebook_metadata import NotebookMetadataExtractor
from app.core.config import get_settings
from app.services.storage.factory import create_storage_service
from datetime import datetime, timedelta
from app.schemas.notebook import NotebookResponse
from botocore.exceptions import ClientError
from app.models.user import User
from app.models.service_account import ServiceAccount
from app.api import deps
import json
import nbformat
import os
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

router = APIRouter()

class NotebookMetadata(BaseModel):
    path: str
    name: str
    description: str
    tags: List[str]
    python_version: str
    requirements: Dict[str, str]
    parameters: List[Dict]
    last_modified: str
    size: int

@router.get("/notebooks", response_model=List[NotebookMetadata])
async def list_notebooks(
    storage: BaseStorageService = Depends(create_storage_service),
    prefix: Optional[str] = "",
    current_principal: Union[User, ServiceAccount] = Depends(deps.get_current_user_or_service_account)
):
    """
    List all available notebook templates
    
    This endpoint lists notebook templates from the configured S3 bucket, 
    using the S3_NOTEBOOK_TEMPLATES_PREFIX setting to filter only template notebooks.
    """
    try:
        # If no prefix is provided, use the notebook templates prefix from settings
        if not prefix:
            prefix = settings.S3_NOTEBOOK_TEMPLATES_PREFIX
        # If a relative prefix is provided, prepend the templates prefix
        elif not prefix.startswith(settings.S3_NOTEBOOK_TEMPLATES_PREFIX):
            prefix = f"{settings.S3_NOTEBOOK_TEMPLATES_PREFIX}/{prefix}"
            
        notebooks = await storage.list_notebooks(prefix)
        result = []
        
        for notebook in notebooks:
            content = await storage.read_notebook(notebook['path'])
            metadata_extractor = NotebookMetadataExtractor(content.read())
            metadata = metadata_extractor.extract_metadata()
            
            result.append(NotebookMetadata(
                path=notebook['path'],
                name=metadata["identity"].get('name', ''),
                description=metadata["identity"].get('description', ''),
                tags=metadata["identity"].get('tags', []),
                python_version=metadata["identity"].get('python_version', ''),
                requirements=metadata.get('requirements', {}),
                parameters=metadata.get('parameters', []),
                last_modified=notebook['last_modified'].isoformat(),
                size=notebook['size']
            ))
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notebooks/download")
async def download_notebook_by_query(
    path: str,
    storage: BaseStorageService = Depends(create_storage_service),
    current_principal: Union[User, ServiceAccount] = Depends(deps.get_current_user_or_service_account)
):
    """Download a specific notebook template using query parameter for the path"""
    # Verify authentication
    if current_principal is None:
        logger.warning(f"Unauthorized access attempt to download notebook: {path}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not path:
        raise HTTPException(status_code=400, detail="Path parameter is required")
    
    logger.info(f"[DOWNLOAD] Received path parameter: {path}")
    
    # Remove leading/trailing slashes
    clean_path = path.strip('/')
    
    # Normalize the path to collapse any '..' or redundant separators
    normalized_path = os.path.normpath(clean_path)
    # Check for directory traversal (if normalized path escapes the intended directory)
    if normalized_path.startswith("..") or ".." in normalized_path:
        logger.error(f"[DOWNLOAD] Invalid path parameter: {normalized_path}")
        raise HTTPException(status_code=400, detail="Invalid path parameter")
    
    logger.info(f"[DOWNLOAD] Using cleaned and normalized path for S3: {normalized_path}")
    
    try:
        # Read the notebook from storage with the normalized path
        content = await storage.read_notebook(normalized_path)
        logger.info(f"[DOWNLOAD] Successfully read notebook content")
        
        # Extract filename from path and enforce .ipynb extension
        filename = normalized_path.split('/')[-1]
        if not filename.endswith('.ipynb'):
            filename = f"{filename}.ipynb"
        logger.info(f"[DOWNLOAD] Using filename: {filename}")
        
        # Return the notebook content directly
        return Response(
            content=content.read(),
            media_type="application/x-ipynb+json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        logger.error(f"[DOWNLOAD] Error in download_notebook_by_query: {str(e)}")
        # Avoid leaking internal details to the client
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/notebooks", response_model=NotebookResponse)
async def upload_notebook(
    file: UploadFile = File(...),
    storage: BaseStorageService = Depends(create_storage_service),
    current_user: User = Depends(deps.get_current_user),
):
    """Upload a notebook template file"""
    try:
        # Read the file content
        content = await file.read()
        
        # Extract metadata from the notebook
        metadata_extractor = NotebookMetadataExtractor(content.decode('utf-8'))
        metadata = metadata_extractor.extract_metadata()
        
        # Upload the notebook to storage using the notebook templates prefix
        path = f"{settings.S3_NOTEBOOK_TEMPLATES_PREFIX}/{file.filename}"
        await storage.write_notebook(path, content)
        
        # Store metadata in database or return it
        return NotebookResponse(
            path=path,
            filename=file.filename,
            metadata=metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notebooks/validate", response_model=NotebookMetadata)
async def validate_notebook(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Validate a notebook template file and extract its metadata without storing it.
    This endpoint allows users to check notebook metadata before committing.
    """
    try:
        # Read the file content
        content = await file.read()
        
        # Extract metadata from the notebook
        metadata_extractor = NotebookMetadataExtractor(content)
        metadata = metadata_extractor.extract_metadata()
        
        # Return metadata without storing the notebook
        # Use a path that includes the templates prefix for consistency
        return NotebookMetadata(
            path=f"{settings.S3_NOTEBOOK_TEMPLATES_PREFIX}/temp/{file.filename}",
            name=metadata["identity"].get('name', file.filename),
            description=metadata["identity"].get('description', ''),
            tags=metadata["identity"].get('tags', []),
            python_version=metadata["identity"].get('python_version', ''),
            requirements=metadata.get('requirements', {}),
            parameters=metadata.get('parameters', []),
            last_modified=datetime.now().isoformat(),
            size=len(content)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notebooks/update-metadata", response_model=NotebookResponse)
async def update_notebook_metadata(
    file: UploadFile = File(...),
    metadata: str = File(...),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update notebook metadata and return the modified notebook for download.
    This endpoint allows users to edit metadata without storing the notebook.
    """
    try:
        # Read the file content
        content = await file.read()
        
        # Parse the metadata
        updated_metadata = json.loads(metadata)
        
        # Load the notebook
        notebook = nbformat.reads(content, as_version=4)
        
        # Ensure notebook_spec exists in metadata
        if 'metadata' not in notebook:
            notebook['metadata'] = {}
        if 'notebook_spec' not in notebook['metadata']:
            notebook['metadata']['notebook_spec'] = {}
        
        # Update identity information
        notebook['metadata']['notebook_spec']['name'] = updated_metadata.get('name', '')
        notebook['metadata']['notebook_spec']['description'] = updated_metadata.get('description', '')
        notebook['metadata']['notebook_spec']['tags'] = updated_metadata.get('tags', [])
        notebook['metadata']['notebook_spec']['python_version'] = updated_metadata.get('python_version', '3.10')
        
        # Update requirements if provided
        if 'requirements' in updated_metadata and updated_metadata['requirements']:
            notebook['metadata']['notebook_spec']['requirements'] = updated_metadata['requirements']
        
        # Convert the notebook back to bytes
        updated_content = nbformat.writes(notebook).encode('utf-8')
        
        # When returning as blob/download, we should just return the raw notebook content
        # instead of wrapping it in a NotebookResponse
        return Response(
            content=updated_content,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={file.filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notebooks/{path:path}", response_model=NotebookMetadata)
async def get_notebook(
    path: str,
    storage: BaseStorageService = Depends(create_storage_service),
    current_principal: Union[User, ServiceAccount] = Depends(deps.get_current_user_or_service_account)
):
    """Get details about a specific notebook template"""
    try:
        # If the path doesn't already include the templates prefix, add it
        if not path.startswith(settings.S3_NOTEBOOK_TEMPLATES_PREFIX):
            full_path = f"{settings.S3_NOTEBOOK_TEMPLATES_PREFIX}/{path}"
        else:
            full_path = path
            
        content = await storage.read_notebook(full_path)
        metadata_extractor = NotebookMetadataExtractor(content.read())
        metadata = metadata_extractor.extract_metadata()
        
        notebook_info = await storage.list_notebooks(full_path)
        if not notebook_info:
            raise HTTPException(status_code=404, detail="Notebook not found")
        
        return NotebookMetadata(
            path=full_path,
            name=metadata["identity"].get('name', path),
            description=metadata["identity"].get('description', ''),
            tags=metadata["identity"].get('tags', []),
            python_version=metadata["identity"].get('python_version', ''),
            requirements=metadata.get('requirements', {}),
            parameters=metadata.get('parameters', []),
            last_modified=notebook_info[0]['last_modified'].isoformat(),
            size=notebook_info[0]['size']
        )   
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notebooks/{path:path}/rate-limit")
async def get_notebook_rate_limit(
    path: str,
    current_principal: Union[User, ServiceAccount] = Depends(deps.get_current_user_or_service_account)
):
    """Get rate limit information for a notebook"""
    try:
        # This implementation will depend on your rate limiting strategy
        # Here's a placeholder that returns basic rate limit info
        return {
            "limit": 10,  # requests per hour
            "remaining": 8,
            "reset": int((datetime.now() + timedelta(hours=1)).timestamp())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
