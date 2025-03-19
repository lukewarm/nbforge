from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import StreamingResponse
import io
import logging
from typing import Optional, Union
import os
import boto3
from botocore.exceptions import ClientError
from app.core.config import get_settings
from app.services.storage.factory import create_storage_service
from app.services.storage.s3_storage import get_s3_client  # Import the get_s3_client function
from app.models.user import User
from app.models.service_account import ServiceAccount
from app.api import deps

settings = get_settings()
logger = logging.getLogger(__name__)

router = APIRouter()

# Remove the direct initialization and use lazy initialization instead
# by importing get_s3_client from s3_storage.py

@router.get("/static/reports/{path:path}")
async def get_static_report(
    path: str,
    current_principal: Union[User, ServiceAccount] = Depends(deps.get_current_user_or_service_account)
):
    """
    Serve static files from S3 storage.
    
    This endpoint retrieves static files like notebooks and HTML reports from S3
    and returns them with the appropriate content type.
    """
    # Explicitly verify authentication
    if current_principal is None:
        logger.warning(f"Unauthorized access attempt to static file: {path}")
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        # Log debugging information
        logger.info(f"Attempting to fetch file from S3: {path}")
        logger.info(f"S3 bucket: {settings.S3_BUCKET}")
        
        # Get the singleton S3 client
        s3 = get_s3_client()
        
        # Get the object from S3
        response = s3.get_object(
            Bucket=settings.S3_BUCKET,
            Key=path
        )
        
        # Read the content and create a streaming response
        content = response['Body'].read()
        
        # Determine content type based on file extension
        content_type = 'application/octet-stream'  # Default content type
        if path.endswith('.html'):
            content_type = 'text/html'
        elif path.endswith('.ipynb'):
            content_type = 'application/x-ipynb+json'
        elif path.endswith('.json'):
            content_type = 'application/json'
        elif path.endswith('.css'):
            content_type = 'text/css'
        elif path.endswith('.js'):
            content_type = 'application/javascript'
        
        # Return the streaming response with the appropriate content type
        return Response(
            content=content,
            media_type=content_type
        )
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == 'NoSuchKey':
            logger.error(f"File not found in S3: {path}")
            raise HTTPException(status_code=404, detail="File not found")
        logger.error(f"S3 ClientError: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving file: {str(e)}")
    except Exception as e:
        logger.error(f"Error fetching file from S3: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving file: {str(e)}") 