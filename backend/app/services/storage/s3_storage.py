from typing import BinaryIO, List, Dict, Optional, Tuple, Any
import boto3
import io
import os
import asyncio
import time
import functools
from botocore.client import Config
from .interface import BaseStorageService
import logging

from app.core.config import get_settings
settings = get_settings()

logger = logging.getLogger(__name__)


# Use lazy initialization for the S3 client to ensure environment variables are loaded
class S3ClientManager:
    """Manager for S3 client that creates the client on first use"""
    
    _instance = None
    
    def __init__(self):
        self._client = None
    
    @property
    def client(self):
        """Get or create the S3 client"""
        if self._client is None:
            # Create the client when first requested, not at module import time
            s3_endpoint_url = os.getenv("S3_ENDPOINT_URL")
            aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            
            self._client = boto3.client(
                's3',
                endpoint_url=s3_endpoint_url,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                config=Config(signature_version='s3v4'),
            )
        return self._client
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# Access the singleton through a function to make mocking easier in tests
def get_s3_client():
    """Get the singleton S3 client"""
    return S3ClientManager.get_instance().client


class LRUCache:
    """Simple LRU cache with TTL support."""

    def __init__(self, maxsize: int = 100, ttl: int = 60):
        """Initialize cache with maximum size and TTL in seconds."""
        self.maxsize = maxsize
        self.ttl = ttl
        self.cache = {}  # key -> (value, timestamp, etag)
        self.access_order = []  # LRU tracking

    def get(self, key: str) -> Tuple[Any, Optional[str]]:
        """Get item from cache and return (value, etag)."""
        if key in self.cache:
            value, timestamp, etag = self.cache[key]
            current_time = time.time()
            
            # Check if item has expired
            if current_time - timestamp > self.ttl:
                self._remove(key)
                return None, None
                
            # Update access order
            self._update_access(key)
            return value, etag
            
        return None, None

    def set(self, key: str, value: Any, etag: Optional[str] = None) -> None:
        """Add item to cache with current timestamp."""
        # If cache is full, evict the least recently used item
        if len(self.cache) >= self.maxsize and key not in self.cache:
            self._evict()
            
        self.cache[key] = (value, time.time(), etag)
        self._update_access(key)

    def _update_access(self, key: str) -> None:
        """Update the access order for the LRU algorithm."""
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)

    def _evict(self) -> None:
        """Evict the least recently used item from the cache."""
        if self.access_order:
            lru_key = self.access_order.pop(0)
            if lru_key in self.cache:
                del self.cache[lru_key]

    def _remove(self, key: str) -> None:
        """Remove an item from the cache."""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_order:
            self.access_order.remove(key)


class S3Storage(BaseStorageService):
    def __init__(self, bucket: str, endpoint_url: Optional[str] = None, cache_size: int = 100, cache_ttl: int = 600):
        """Initialize S3 client with optional endpoint for S3-compatible storage"""
        # Get the S3 client from the manager - this will initialize it if needed
        self.s3 = get_s3_client()
        self.bucket = bucket
        
        # Initialize cache
        self.cache = LRUCache(maxsize=cache_size, ttl=cache_ttl)

    async def list_notebooks(self, prefix: str = "") -> List[Dict]:
        """List notebooks in storage asynchronously"""
        # Run the blocking S3 operation in a thread pool
        response = await asyncio.to_thread(
            self.s3.list_objects_v2,
            Bucket=self.bucket,
            Prefix=prefix
        )
        
        notebooks = []
        for obj in response.get('Contents', []):
            if obj['Key'].endswith('.ipynb'):
                notebooks.append({
                    'path': obj['Key'],
                    'last_modified': obj['LastModified'],
                    'size': obj['Size']
                })
        return notebooks

    async def read_notebook(self, path: str) -> BinaryIO:
        """
        Read notebook from storage asynchronously with caching
        """
        if not path:
            raise ValueError("Path cannot be empty")
            
        logger.info(f"[S3] Reading notebook with path: {path}")
        
        # Check cache first
        cached_content, cached_etag = self.cache.get(path)
        
        if cached_content is not None:
            logger.info(f"[S3] Found cached version of {path}")
            try:
                # If we have a cached version, check if it's still valid using head_object
                head_response = await asyncio.to_thread(
                    self.s3.head_object,
                    Bucket=self.bucket,
                    Key=path
                )
                
                current_etag = head_response.get('ETag')
                
                # If ETag matches, use cached version
                if current_etag == cached_etag:
                    logger.info(f"[S3] Cache is valid for {path}, using cached version")
                    # Return a new BytesIO to avoid modifying the cached version
                    return io.BytesIO(cached_content.getvalue())
                
                logger.info(f"[S3] Cache is outdated for {path}, fetching new version")
            except Exception as e:
                logger.warning(f"[S3] Error checking cache validity for {path}: {str(e)}")
                # On any error, just proceed to fetch the object
                pass
        
        # If not in cache or cache is invalid, fetch from S3
        try:
            # Log the exact S3 parameters we're using
            logger.info(f"[S3] Making GetObject request: bucket={self.bucket}, key={path}")
            
            response = await asyncio.to_thread(
                self.s3.get_object,
                Bucket=self.bucket,
                Key=path
            )
            
            # Read the content
            content = io.BytesIO(response['Body'].read())
            content_length = len(content.getvalue())
            logger.info(f"[S3] Successfully read {content_length} bytes from S3 for {path}")
            
            # Get ETag for cache validation
            etag = response.get('ETag')
            
            # Cache the response
            cache_copy = io.BytesIO(content.getvalue())
            self.cache.set(path, cache_copy, etag)
            
            # Reset the position for the content being returned
            content.seek(0)
            return content
        except Exception as e:
            error_msg = f"[S3] Error reading notebook: bucket={self.bucket}, key={path}, error={str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    async def write_notebook(self, path: str, content: BinaryIO) -> str:
        """Write notebook to storage asynchronously and invalidate cache"""
        await asyncio.to_thread(
            self.s3.upload_fileobj,
            content,
            self.bucket,
            path
        )
        
        # Invalidate cache by removing the entry
        self.cache._remove(path)
        
        return f"s3://{self.bucket}/{path}"

    async def get_presigned_url(self, path: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for temporary access asynchronously"""
        url = await asyncio.to_thread(
            self.s3.generate_presigned_url,
            'get_object',
            Params={'Bucket': self.bucket, 'Key': path},
            ExpiresIn=expires_in
        )
        return url

    async def delete_notebook(self, path: str) -> None:
        """Delete a notebook from storage asynchronously and invalidate cache"""
        await asyncio.to_thread(
            self.s3.delete_object,
            Bucket=self.bucket,
            Key=path
        )
        
        # Invalidate cache by removing the entry
        self.cache._remove(path) 