from typing import Dict, Optional, List
from kubernetes import client, config
from .base import BaseBatchExecutor
import logging
import json
import asyncio
from app.core.config import get_settings
import os

settings = get_settings()
logger = logging.getLogger(__name__)

class K8sExecutor(BaseBatchExecutor):
    def __init__(self):
        """Initialize Kubernetes client"""
        if os.getenv('KUBERNETES_SERVICE_HOST'):
            # In-cluster config
            config.load_incluster_config()
        else:
            # Local development
            config.load_kube_config()
        self.batch_v1 = client.BatchV1Api()
        self.core_v1 = client.CoreV1Api()
        self.namespace = settings.K8S_NAMESPACE

    async def create_job(
        self,
        notebook_path: str,
        parameters: Dict,
        python_version: str,
        job_name: str,
        cpu_milli: int = None,
        memory_mib: int = None,
        output_bucket: Optional[str] = None,
        requirements: Optional[List[str]] = None,
        callback_token: Optional[str] = None
    ) -> str:
        """Create a Kubernetes job to execute a notebook"""
        try:
            # Set default resources if not provided
            cpu_milli = cpu_milli or settings.DEFAULT_CPU_MILLI
            memory_mib = memory_mib or settings.DEFAULT_MEMORY_MIB
            
            # Use the bucket from settings if not provided
            s3_bucket = output_bucket or settings.S3_BUCKET
            
            # Create resource names
            config_map_name = f"nbforge-job-{job_name}-config"
            secret_name = f"nbforge-job-{job_name}-secret"
            
            # Create ConfigMap and Secret
            await self._create_config_map(job_name, config_map_name, notebook_path, 
                                         parameters, requirements, s3_bucket, python_version)
            await self._create_secret(job_name, secret_name)
            
            # Create job
            env = self._prepare_env_vars(notebook_path, parameters, python_version, 
                                        job_name, s3_bucket, requirements, callback_token)
            job_spec = self._create_job_spec(job_name, config_map_name, secret_name, 
                                           env, cpu_milli, memory_mib)
            
            # Create the job in Kubernetes - use job_spec directly
            job_response = await self._create_job_async(job_spec)
            
            # Set the job as the owner of the ConfigMap for garbage collection
            await self._set_owner_reference(job_response, config_map_name, config_map_name)
            
            return job_name
        except Exception as e:
            # Clean up resources if job creation fails
            await self._cleanup_resources(job_name, config_map_name, secret_name)
            logger.error(f"Failed to create job: {str(e)}")
            raise

    async def _create_config_map(self, job_name: str, config_map_name: str, 
                               notebook_path: str, parameters: Dict, 
                               requirements: Optional[List[str]], s3_bucket: str,
                               python_version: str) -> None:
        """Create a ConfigMap for job configuration"""
        # Format parameters and requirements as JSON strings
        parameters_json = json.dumps(parameters)
        requirements_json = "[]"
        if requirements:
            requirements_json = json.dumps(requirements)
        
        # Create ConfigMap data
        config_data = {
            "NOTEBOOK_PATH": notebook_path,
            "PARAMETERS": parameters_json,
            "REQUIREMENTS": requirements_json,
            "JOB_ID": job_name,
            "S3_BUCKET": s3_bucket,
            "API_URL": settings.API_URL,
            "PYTHON_VERSION": python_version,
            "OUTPUT_PATH": f"outputs/{job_name}",
            "EXTRACT_JSON_OUTPUTS": "true"
        }
        
        if settings.S3_ENDPOINT_URL:
            config_data["S3_ENDPOINT_URL"] = settings.S3_ENDPOINT_URL
        
        # Create a ConfigMap
        config_map = client.V1ConfigMap(
            metadata=client.V1ObjectMeta(
                name=config_map_name,
                namespace=self.namespace,
                labels={
                    "app": "nbforge",
                    "job-name": job_name
                }
            ),
            data=config_data
        )
        
        # Create the ConfigMap
        logger.info(f"Creating ConfigMap {config_map_name} for job {job_name}")
        await asyncio.to_thread(
            self.core_v1.create_namespaced_config_map,
            self.namespace,
            config_map
        )
        return config_map

    async def _create_secret(self, job_name: str, secret_name: str) -> None:
        """Create a Secret for sensitive information"""
        secret = client.V1Secret(
            metadata=client.V1ObjectMeta(
                name=secret_name,
                namespace=self.namespace
            ),
            string_data={
                "AWS_ACCESS_KEY_ID": settings.AWS_ACCESS_KEY_ID,
                "AWS_SECRET_ACCESS_KEY": settings.AWS_SECRET_ACCESS_KEY
            }
        )
        
        # Create the secret
        await asyncio.to_thread(
            self.core_v1.create_namespaced_secret,
            self.namespace,
            secret
        )

    def _prepare_env_vars(self, notebook_path: str, parameters: Dict, 
                         python_version: str, job_name: str, s3_bucket: str,
                         requirements: Optional[List[str]], callback_token: Optional[str]) -> List[Dict]:
        """Prepare environment variables for the container"""
        env = [
            {"name": "NOTEBOOK_PATH", "value": notebook_path},
            {"name": "PARAMETERS", "value": json.dumps(parameters)},
            {"name": "PYTHON_VERSION", "value": python_version},
            {"name": "JOB_ID", "value": job_name},
            {"name": "S3_BUCKET", "value": s3_bucket},
            {"name": "AWS_ACCESS_KEY_ID", "value": settings.AWS_ACCESS_KEY_ID},
            {"name": "AWS_SECRET_ACCESS_KEY", "value": settings.AWS_SECRET_ACCESS_KEY}
        ]
        
        # Add S3 endpoint if configured (for MinIO)
        if settings.S3_ENDPOINT_URL:
            env.append({"name": "S3_ENDPOINT_URL", "value": settings.S3_ENDPOINT_URL})
            
        # Add callback URL
        if settings.API_URL:
            env.append({"name": "API_URL", "value": settings.API_URL})
            
        # Add callback token if provided
        if callback_token:
            env.append({"name": "CALLBACK_TOKEN", "value": callback_token})

        # Add requirements if provided
        if requirements:
            env.append({"name": "REQUIREMENTS", "value": json.dumps(requirements)})
        
        return env

    def _create_job_spec(self, job_name: str, config_map_name: str, secret_name: str, 
                        env: List[Dict], cpu_milli: int, memory_mib: int) -> Dict:
        """
        Create the job specification with TTL settings for automatic cleanup
        
        Args:
            job_name: The base name for the job
            config_map_name: Name of the ConfigMap containing configuration
            secret_name: Name of the Secret containing sensitive data
            env: List of environment variables
            cpu_milli: CPU request in millicores
            memory_mib: Memory request in MiB
            
        Returns:
            Dict: The complete job specification
        """
        # Format CPU and memory for Kubernetes
        cpu_request = f"{cpu_milli}m"
        memory_request = f"{memory_mib}Mi"
        memory_limit = memory_request  # Only set limit for memory as per best practices
        
        # Set TTL for automatic cleanup - jobs will be deleted after this many seconds
        # Default: 24 hours (86400 seconds)
        ttl_seconds_after_finished = 86400 * 3
        
        job_name_full = f"notebook-execution-{job_name}"
        return {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": job_name_full,
                "labels": {
                    "app": "nbforge",
                    "component": "notebook-runner",
                    "execution-id": job_name
                }
            },
            "spec": {
                "ttlSecondsAfterFinished": ttl_seconds_after_finished,  # Add TTL for automatic cleanup
                "backoffLimit": 0,  # Disable retries
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "nbforge",
                            "component": "notebook-runner",
                            "job-name": job_name_full,
                            "execution-id": job_name
                        }
                    },
                    "spec": {
                        "securityContext": {
                            "runAsUser": 1000,
                            "runAsGroup": 1000,
                            "fsGroup": 1000,
                        },
                        "containers": [{
                            "name": "notebook-runner",
                            "image": settings.NOTEBOOK_RUNNER_IMAGE,
                            "imagePullPolicy": "IfNotPresent",
                            "envFrom": [
                                {"configMapRef": {"name": config_map_name}},
                                {"secretRef": {"name": secret_name}}
                            ],                                
                            "resources": {
                                "requests": {
                                    "cpu": cpu_request,
                                    "memory": memory_request
                                },
                                "limits": {
                                    "memory": memory_limit
                                }
                            },
                            "securityContext": {
                                "allowPrivilegeEscalation": False
                            },                            
                            "env": env
                        }],
                        "restartPolicy": "Never",
                        "serviceAccountName": "default"
                    }
                }
            }
        }

    async def _set_owner_reference(self, job_response, config_map_name: str, config_map) -> None:
        """Set the job as the owner of the ConfigMap for garbage collection"""
        try:
            owner_ref = client.V1OwnerReference(
                api_version="batch/v1",
                kind="Job",
                name=job_response.metadata.name,
                uid=job_response.metadata.uid,
                block_owner_deletion=True
            )
            
            config_map.metadata.owner_references = [owner_ref]
            await asyncio.to_thread(
                self.core_v1.replace_namespaced_config_map,
                config_map_name,
                self.namespace,
                config_map
            )
        except Exception as e:
            logger.warning(f"Failed to set owner reference for ConfigMap: {str(e)}")

    async def _cleanup_resources(self, job_name: str, config_map_name: str, secret_name: str) -> None:
        """Clean up resources if job creation fails"""
        # Clean up the ConfigMap
        try:
            await asyncio.to_thread(
                self.core_v1.delete_namespaced_config_map,
                config_map_name,
                self.namespace
            )
        except Exception as cm_error:
            logger.warning(f"Failed to clean up ConfigMap: {str(cm_error)}")
        
        # Clean up the Secret
        try:
            await asyncio.to_thread(
                self.core_v1.delete_namespaced_secret,
                secret_name,
                self.namespace
            )
        except Exception as sm_error:
            logger.warning(f"Failed to clean up Secret: {str(sm_error)}")

    async def _create_job_async(self, job) -> client.V1Job:
        """Async wrapper for kubernetes client"""
        return await asyncio.to_thread(
            self.batch_v1.create_namespaced_job,
            self.namespace,
            job
        )

    async def get_job_status(self, job_name: str) -> Dict:
        """
        Get status of a Kubernetes job
        
        Maps Kubernetes job states to NBForge execution statuses:
        - If active: 'running'
        - If succeeded: 'completed'
        - If failed: 'failed'
        - Otherwise: 'pending'
        """
        try:
            response = await self._get_job_status_async(job_name)
            
            status = "pending"
            if response.status.active:
                status = "running"
            elif response.status.succeeded:
                status = "completed"
            elif response.status.failed:
                status = "failed"
                
            return {
                "status": status,
                "start_time": response.status.start_time,
                "completion_time": response.status.completion_time
            }
        except Exception as e:
            logger.error(f"Failed to get job status: {str(e)}")
            raise

    async def _get_job_status_async(self, job_name: str) -> client.V1Job:
        """Async wrapper for getting job status"""
        logger.info(f"Getting status for job: {job_name} in namespace: {self.namespace}")
        try:
            result = await asyncio.to_thread(
                self.batch_v1.read_namespaced_job_status,
                job_name,
                self.namespace
            )
            logger.info(f"Successfully found job {job_name} with status: {result.status}")
            return result
        except Exception as e:
            logger.error(f"Error getting job status for {job_name} in namespace {self.namespace}: {str(e)}")
            # Log more details about the error to understand its type and structure
            logger.error(f"Error type: {type(e).__name__}")
            if hasattr(e, 'status') and hasattr(e, 'reason'):
                logger.error(f"API error: {getattr(e, 'status', None)} - {getattr(e, 'reason', None)}")
            raise

    async def cancel_job(self, job_name: str) -> bool:
        """
        Cancel a Kubernetes job and clean up associated resources
        
        Args:
            job_name: The name of the job to cancel (including 'notebook-execution-' prefix)
            
        Returns:
            bool: True if cancellation was successful, False otherwise
        """
        try:
            # Extract the execution ID from the job name (if it has the prefix, otherwise use as is)
            execution_id = job_name
            if job_name.startswith("notebook-execution-"):
                execution_id = job_name.replace("notebook-execution-", "")
            else:
                # If the job name doesn't have the prefix, add it
                job_name = f"notebook-execution-{job_name}"
            
            logger.info(f"Attempting to cancel job {job_name} (execution ID: {execution_id}) in namespace {self.namespace}")
            
            # Check if the job exists and get its status
            job_exists = False
            job_already_completed = False
            
            try:
                logger.info(f"Checking if job {job_name} exists in namespace {self.namespace}...")
                # List all jobs in the namespace to verify what's actually there
                all_jobs = await asyncio.to_thread(
                    self.batch_v1.list_namespaced_job,
                    self.namespace
                )
                job_names = [job.metadata.name for job in all_jobs.items]
                logger.info(f"Found {len(job_names)} jobs in namespace {self.namespace}.")
                
                # Check if our job is in the list
                if job_name in job_names:
                    job_exists = True
                    logger.info(f"Job {job_name} found in the namespace.")
                    
                    # Try to get the specific job status
                    job_status = await asyncio.to_thread(
                        self.batch_v1.read_namespaced_job_status,
                        job_name,
                        self.namespace
                    )
                    
                    # Check if job is already completed or failed
                    if job_status.status.succeeded or job_status.status.failed:
                        job_already_completed = True
                        status = "succeeded" if job_status.status.succeeded else "failed"
                        logger.info(f"Job {job_name} already {status} - nothing to cancel")
                        
                        # Even for completed jobs, we might want to clean up resources
                        # Only return false to indicate that a cancellation wasn't necessary
                        try:
                            # Clean up ConfigMap and Secret
                            await self._cleanup_resources(
                                job_name, 
                                f"nbforge-job-{execution_id}-config",
                                f"nbforge-job-{execution_id}-secret"
                            )
                        except Exception as cleanup_err:
                            logger.warning(f"Failed to clean up resources for completed job: {str(cleanup_err)}")
                            
                        return False
                    
                    # Log job status details
                    logger.info(f"Job status: active={job_status.status.active}, succeeded={job_status.status.succeeded}, failed={job_status.status.failed}")
                else:
                    logger.error(f"Job {job_name} not found in the list of jobs in namespace {self.namespace}")
                    return False
                    
            except Exception as e:
                logger.error(f"Failed to find job {job_name}: {str(e)}")
                return False
                
            # Only proceed with cancellation if the job exists and is not already completed
            if job_exists and not job_already_completed:
                # First delete the job
                logger.info(f"Proceeding to delete job {job_name}")
                await self._delete_job_async(job_name)
                logger.info(f"Successfully deleted job {job_name}")
                
                # Then try to delete the ConfigMap
                config_map_name = f"nbforge-job-{execution_id}-config"
                try:
                    logger.info(f"Deleting ConfigMap {config_map_name}")
                    await asyncio.to_thread(
                        self.core_v1.delete_namespaced_config_map,
                        config_map_name,
                        self.namespace
                    )
                    logger.info(f"Successfully deleted ConfigMap {config_map_name}")
                except Exception as e:
                    logger.warning(f"Failed to delete ConfigMap {config_map_name}: {str(e)}")
                
                # Finally try to delete the Secret
                secret_name = f"nbforge-job-{execution_id}-secret"
                try:
                    logger.info(f"Deleting Secret {secret_name}")
                    await asyncio.to_thread(
                        self.core_v1.delete_namespaced_secret,
                        secret_name,
                        self.namespace
                    )
                    logger.info(f"Successfully deleted Secret {secret_name}")
                except Exception as e:
                    logger.warning(f"Failed to delete Secret {secret_name}: {str(e)}")
                    
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to cancel job {job_name}: {str(e)}")
            # Get stack trace for debugging
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    async def _delete_job_async(self, job_name: str) -> None:
        """Async wrapper for deleting job"""
        await asyncio.to_thread(
            self.batch_v1.delete_namespaced_job,
            job_name,
            self.namespace,
            body=client.V1DeleteOptions(propagation_policy='Foreground')
        )
            
    async def list_jobs(self) -> List[Dict]:
        """List all jobs"""
        try:
            job_list = await asyncio.to_thread(
                self.batch_v1.list_namespaced_job,
                self.namespace,
                label_selector="app=nbforge,component=notebook-runner"
            )
            
            result = []
            for job in job_list.items:
                job_name = job.metadata.name.replace("notebook-execution-", "")
                status = "pending"
                if job.status.active:
                    status = "running"
                elif job.status.succeeded:
                    status = "completed"
                elif job.status.failed:
                    status = "failed"
                
                result.append({
                    "name": job_name,
                    "status": status,
                    "start_time": job.status.start_time,
                    "completion_time": job.status.completion_time
                })
                
            return result
        except Exception as e:
            logger.error(f"Failed to list jobs: {str(e)}")
            raise 