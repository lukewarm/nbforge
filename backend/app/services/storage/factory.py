from typing import Optional
from .s3_storage import S3Storage
from .interface import BaseStorageService
from app.core.config import get_settings

settings = get_settings()

def create_storage_service() -> BaseStorageService:
    """Create S3 storage service with appropriate configuration"""
    return S3Storage(
        bucket=settings.S3_BUCKET,
        endpoint_url=settings.S3_ENDPOINT_URL
    ) 