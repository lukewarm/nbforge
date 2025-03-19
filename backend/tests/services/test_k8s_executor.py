from unittest import TestCase
from unittest.mock import MagicMock, AsyncMock

class TestK8sExecutor(TestCase):
    def setUp(self):
        self.executor = K8sExecutor()

    async def test_create_job(self):
        """Test creating a Kubernetes job"""
        # Mock the Kubernetes client
        self.executor.batch_v1 = MagicMock()
        self.executor._create_job_async = AsyncMock()
        
        # Call the method
        job_name = await self.executor.create_job(
            notebook_path="test.ipynb",
            parameters={"param1": "value1"},
            python_version="3.12",
            job_name="test-job",
            cpu_milli=2000,
            memory_mib=4096
        )
        
        # Verify the job was created
        self.assertEqual(job_name, "test-job")
        self.executor._create_job_async.assert_called_once()
        
        # Verify the job spec contains the notebook runner image
        job_spec = self.executor._create_job_async.call_args[0][0]
        self.assertEqual(
            job_spec['spec']['template']['spec']['containers'][0]['image'],
            "nbforge/notebook-runner:latest"
        ) 