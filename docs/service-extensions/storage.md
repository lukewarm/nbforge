# Storage Service

The Storage Service provides a unified interface for storing, retrieving, and managing notebooks across different cloud storage providers. Currently, it implements S3-compatible storage, but the architecture is designed to be extended with additional providers such as Google Cloud Storage (GCS) or Azure Blob Storage.

## Architecture

The storage service follows a provider-based architecture:

1. **Interface** (`BaseStorageService`): Defines the contract that all storage providers must implement.
2. **Implementations**: Provider-specific classes that implement the `BaseStorageService` interface.
   - `S3Storage`: Current implementation for S3-compatible storage
3. **Factory** (`create_storage_service`): Creates and configures the appropriate storage service implementation based on application settings.

## Extending with New Providers

To add support for a new storage provider (e.g., Google Cloud Storage, Azure Blob Storage), follow these steps:

### 1. Create a New Provider Class

Create a new class that inherits from `BaseStorageService` and implements all required methods:

```python
# Example: gcs_storage.py
from io import BytesIO
from typing import BinaryIO, List, Dict
from google.cloud import storage

from backend.app.services.storage.interface import BaseStorageService

class GCSStorage(BaseStorageService):
    """Google Cloud Storage implementation"""
    
    def __init__(self, bucket: str, **kwargs):
        """Initialize GCS storage with the specified bucket"""
        self.bucket_name = bucket
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket)
        # Add any additional configuration
        
    async def list_notebooks(self, prefix: str = "") -> List[Dict]:
        """List all notebooks with the given prefix"""
        blobs = self.bucket.list_blobs(prefix=prefix)
        notebooks = []
        for blob in blobs:
            notebooks.append({
                "path": blob.name,
                "last_modified": blob.updated,
                "size": blob.size
            })
        return notebooks
    
    async def read_notebook(self, path: str) -> BinaryIO:
        """Read a notebook from storage"""
        blob = self.bucket.blob(path)
        content = BytesIO()
        blob.download_to_file(content)
        content.seek(0)
        return content
    
    async def write_notebook(self, path: str, content: BinaryIO) -> str:
        """Write a notebook to storage"""
        blob = self.bucket.blob(path)
        blob.upload_from_file(content)
        return path
    
    async def delete_notebook(self, path: str) -> None:
        """Delete a notebook from storage"""
        blob = self.bucket.blob(path)
        blob.delete()
    
    async def get_presigned_url(self, path: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for temporary access"""
        blob = self.bucket.blob(path)
        return blob.generate_signed_url(
            version="v4",
            expiration=expires_in,
            method="GET"
        )
```

### 2. Update the Factory Function

Modify the `factory.py` file to include support for your new provider:

```python
from backend.app.core.config import settings
from backend.app.services.storage.interface import BaseStorageService
from backend.app.services.storage.s3_storage import S3Storage
from backend.app.services.storage.gcs_storage import GCSStorage  # Import your new provider

def create_storage_service() -> BaseStorageService:
    """Create storage service with appropriate configuration"""
    storage_provider = settings.STORAGE_PROVIDER.lower()
    
    if storage_provider == "s3":
        return S3Storage(
            bucket=settings.S3_BUCKET,
            endpoint_url=settings.S3_ENDPOINT_URL
        )
    elif storage_provider == "gcs":
        return GCSStorage(
            bucket=settings.GCS_BUCKET
        )
    else:
        raise ValueError(f"Unsupported storage provider: {storage_provider}")
```

### 3. Update Configuration

Add the necessary configuration settings to `config.py`:

```python
# Storage settings
STORAGE_PROVIDER: str = os.getenv("STORAGE_PROVIDER", "s3")
S3_BUCKET: str = os.getenv("S3_BUCKET", "nbforge")
S3_ENDPOINT_URL: str = os.getenv("S3_ENDPOINT_URL")
# New provider settings
GCS_BUCKET: str = os.getenv("GCS_BUCKET", "nbforge")
```

## Requirements for Provider Implementation

When implementing a new storage provider, ensure:

1. **Interface Compliance**: Implement all abstract methods from `BaseStorageService`.
2. **Error Handling**: Implement robust error handling and translate provider-specific errors into appropriate application exceptions.
3. **Async Support**: Ensure all methods support asyncio, even if the underlying provider SDK is synchronous.
4. **Permissions**: Handle authentication and authorization appropriately.
5. **Performance**: Consider implementing caching or other optimizations for frequently accessed resources.

## Best Practices

1. **Connection Pooling**: Reuse client connections whenever possible to avoid overhead.
2. **Lazy Initialization**: Initialize the client on first use rather than at object creation.
3. **Detailed Logging**: Log operations and errors at appropriate levels.
4. **Rate Limiting**: Implement backoff and retry logic for API rate limits.
5. **Mimetype Handling**: Ensure proper content types are set for uploaded notebooks.
6. **Testing**: Create comprehensive tests for your provider implementation.

## Development Tips

1. **Local Development**: Consider using local emulators (e.g., LocalStack for S3, Azurite for Azure, GCS emulator) for testing without cloud dependencies.
2. **Environment Variables**: Use environment variables for credentials and endpoints.
3. **Package Dependencies**: Add required provider SDK dependencies to requirements.txt.
4. **Documentation**: Update deployment documentation with new environment variables. 