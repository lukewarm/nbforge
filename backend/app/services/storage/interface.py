from typing import BinaryIO, List, Dict, Optional
from abc import ABC, abstractmethod

class BaseStorageService(ABC):
    """Base interface for storage services"""
    
    @abstractmethod
    async def list_notebooks(self, prefix: str = "") -> List[Dict]:
        """List all notebooks with the given prefix"""
        pass
    
    @abstractmethod
    async def read_notebook(self, path: str) -> BinaryIO:
        """Read a notebook from storage"""
        pass
    
    @abstractmethod
    async def write_notebook(self, path: str, content: BinaryIO) -> str:
        """Write a notebook to storage"""
        pass
    
    @abstractmethod
    async def delete_notebook(self, path: str) -> None:
        """Delete a notebook from storage"""
        pass
    
    @abstractmethod
    async def get_presigned_url(self, path: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for temporary access"""
        pass

    async def check_exists(self, path: str) -> bool:
        """
        Check if a notebook exists
        
        Args:
            path: Path to the notebook
            
        Returns:
            True if notebook exists, False otherwise
        """
        ...
        
    async def download_notebook(self, path: str) -> bytes:
        """
        Download a notebook from storage and return its contents as bytes
        
        This is a convenience method that wraps read_notebook
        
        Args:
            path: Path to the notebook
            
        Returns:
            Notebook content as bytes
        """
        content = await self.read_notebook(path)
        return content.getvalue() 