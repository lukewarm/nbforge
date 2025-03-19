from abc import ABC, abstractmethod
from typing import Dict, Optional, List

class BaseBatchExecutor(ABC):
    @abstractmethod
    async def create_job(
        self,
        notebook_path: str,
        parameters: Dict,
        python_version: str,
        job_name: str,
        cpu_milli: int = 4000,
        memory_mib: int = 16384,
        output_bucket: Optional[str] = None,
        requirements: Optional[List[str]] = None,
        callback_token: Optional[str] = None
    ) -> str:
        """Create a job to execute the notebook"""
        pass

    @abstractmethod
    async def get_job_status(self, job_name: str) -> Dict:
        """Get status of a job"""
        pass

    @abstractmethod
    async def list_jobs(self) -> List[Dict]:
        """List all jobs"""
        pass

    @abstractmethod
    async def cancel_job(self, job_name: str) -> bool:
        """Cancel a job"""
        pass 