#!/usr/bin/env python
"""
Notebook Runner

This script executes Jupyter notebooks with parameterization based on the
NBForge specification. It handles Python version selection,
and result output.
"""

import os
import sys
import json
import logging
import argparse
import subprocess
import uuid
import requests
from pathlib import Path
import tempfile
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter
import papermill as pm
import boto3
from botocore.exceptions import ClientError
import time
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Execute Jupyter notebooks with parameters')
    parser.add_argument('--notebook', required=False, help='Path to the notebook file')
    parser.add_argument('--output-dir', default='/outputs', help='Output directory')
    parser.add_argument('--parameters', default='{}', help='JSON string of parameters')
    parser.add_argument('--python-version', default='3.10', help='Python version to use')
    parser.add_argument('--requirements', default='{}', help='JSON string of requirements')
    parser.add_argument('--job-id', required=False, help='Unique job identifier')
    return parser.parse_args()


def get_s3_client():
    """Create and configure S3 client from environment variables"""
    # Check both naming conventions for S3 credentials
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    s3_endpoint_url = os.environ.get('S3_ENDPOINT_URL')
    
    if not aws_access_key_id or not aws_secret_access_key:
        logger.error("Missing S3 credentials. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
        sys.exit(1)
    
    # Configure S3 client
    s3_config = {
        'aws_access_key_id': aws_access_key_id,
        'aws_secret_access_key': aws_secret_access_key,
        'config': boto3.session.Config(signature_version='s3v4')
    }
    
    # Add endpoint URL for MinIO or custom S3 endpoints
    if s3_endpoint_url:
        s3_config['endpoint_url'] = s3_endpoint_url

    try:
        s3_client = boto3.client('s3', **s3_config)
        return s3_client
    except Exception as e:
        logger.error(f"Failed to create S3 client: {str(e)}")
        sys.exit(1)


def download_notebook_from_s3(s3_client, bucket, notebook_path, local_path):
    """Download notebook from S3 bucket to local filesystem"""
    logger.info(f"Downloading notebook from s3://{bucket}/{notebook_path} to {local_path}")
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Download notebook from S3
        s3_client.download_file(bucket, notebook_path, local_path)
        logger.info(f"Successfully downloaded notebook: {local_path}")
        return True
    except ClientError as e:
        logger.error(f"Failed to download notebook from S3: {str(e)}")
        sys.exit(1)


def upload_to_s3(s3_client, local_path, bucket, s3_key):
    """Upload a file to S3 bucket"""
    logger.info(f"Uploading {local_path} to s3://{bucket}/{s3_key}")
    
    try:
        s3_client.upload_file(local_path, bucket, s3_key)
        logger.info(f"Successfully uploaded to s3://{bucket}/{s3_key}")
        return True
    except ClientError as e:
        logger.error(f"Failed to upload to S3: {str(e)}")
        return False


def report_status(status, job_id, details=None):
    """
    Report job status to backend API
    
    Status transitions in the notebook runner:
    - 'running': When the job starts executing
    - 'completed': When execution succeeds
    - 'failed': When execution encounters an error
    
    These status updates are sent back to the API and recorded in the database.
    """
    api_url = os.environ.get('API_URL')
    callback_token = os.environ.get('CALLBACK_TOKEN')
    
    if not api_url:
        logger.warning("API_URL not set. Skipping status reporting.")
        return False
    
    url = f"{api_url}/executions/{job_id}/status"
    
    headers = {
        'Content-Type': 'application/json',
        'X-Callback-Token': callback_token
    }
    
    # Match the ExecutionStatusUpdate schema
    data = {
        'status': status,
    }
    
    # If this is a running status, add start_time
    if status == 'running':
        data['start_time'] = datetime.datetime.now().isoformat()
    
    # If this is a completed or failed status, add end_time
    if status in ['completed', 'failed']:
        data['end_time'] = datetime.datetime.now().isoformat()
    
    # Add error message if present in details
    if details and 'error' in details:
        data['error'] = details['error']
    
    # Add output paths if present in details
    if details and 'output_notebook' in details:
        data['output_notebook'] = details['output_notebook']
    
    if details and 'output_html' in details:
        data['output_html'] = details['output_html']
    
    # Add outputs if present
    if details and 'outputs' in details:
        data['outputs'] = details['outputs']
    
    import time

    max_retries = 5
    backoff_factor = 10

    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200 or response.status_code == 204:
                logger.info(f"Successfully reported status '{status}' for job {job_id}")
                return True
            else:
                logger.warning(f"Failed to report status. API responded with: {response.status_code}")
                return False
        except Exception as e:
            logger.warning(f"Error reporting status: {str(e)}")
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt + 1
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return False

def select_python_environment(python_version):
    """Select the appropriate Jupyter kernel based on version
    
    The values need to match the available kernels installed in the Dockerfile.
    The backend should also be updated to request only one of the available kernels.
    """
    version_map = {
        '3.10': ('python3.10', '/home/nbforge/venv310/bin/python'),
        '3.12': ('python3.12', '/home/nbforge/venv312/bin/python'),
    }
    
    # Default to the latest version if not found
    kernel_name, python_path = version_map.get(python_version, ('python3.10', '/home/nbforge/venv310/bin/python'))
    
    return kernel_name, python_path


def install_requirements(requirements, python_path):
    """Install custom requirements using the selected Python environment"""
    if not requirements:
        return
    
    logger.info(f"Installing custom requirements: {requirements}")
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
        for package, version in requirements.items():
            if version == '*':
                tmp.write(f"{package}\n")
            else:
                tmp.write(f"{package}=={version}\n")
        tmp_path = tmp.name
    
    try:
        # Install requirements using the selected Python environment
        cmd = [python_path, '-m', 'pip', 'install', '-r', tmp_path]
        logger.info(f"Running: {' '.join(cmd)}")
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install requirements: {e}")
        raise
    finally:
        os.unlink(tmp_path)


def execute_notebook(notebook_path, output_path, parameters, kernel_name):
    """Execute notebook with parameters using papermill"""
    logger.info(f"Executing notebook: {notebook_path}")
    
    # Log parameters with their types in detail
    logger.info(f"Parameters (with types):")
    for name, value in parameters.items():
        value_type = type(value).__name__
        value_repr = repr(value)
        logger.info(f"  {name}: {value_repr} (Python type: {value_type})")
    
    logger.info(f"Using kernel: {kernel_name}")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        # Execute notebook with papermill
        pm.execute_notebook(
            notebook_path,
            output_path,
            parameters=parameters,
            kernel_name=kernel_name,
            prepare_only=False
        )
        logger.info(f"Notebook executed successfully. Output saved to: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to execute notebook: {e}")
        raise


def convert_notebook_to_html(notebook_path, html_path):
    """Convert executed notebook to HTML with only outputs visible"""
    logger.info(f"Converting notebook to HTML: {notebook_path}")
    
    # Load the notebook
    with open(notebook_path, 'r') as f:
        notebook = nbformat.read(f, as_version=4)
    
    # Create HTML exporter with custom configuration
    html_exporter = HTMLExporter()
    html_exporter.template_name = 'classic'
    
    # Configure the exporter to exclude input cells
    html_exporter.exclude_input = True
    html_exporter.exclude_input_prompt = True
    html_exporter.exclude_output_prompt = True
    
    # Export to HTML
    (body, resources) = html_exporter.from_notebook_node(notebook)
    
    # Write HTML to file
    with open(html_path, 'w') as f:
        f.write(body)
    
    logger.info(f"HTML output (without code cells) saved to: {html_path}")


def extract_outputs(notebook_path):
    """Extract cell outputs from the executed notebook"""
    outputs = {}
    
    with open(notebook_path, 'r') as f:
        notebook = nbformat.read(f, as_version=4)
    
    for i, cell in enumerate(notebook.cells):
        if cell.cell_type == 'code' and hasattr(cell, 'outputs') and cell.outputs:
            for j, output in enumerate(cell.outputs):
                if output.output_type == 'execute_result' or output.output_type == 'display_data':
                    if 'data' in output and 'text/plain' in output.data:
                        key = f"cell_{i+1}_output_{j+1}"
                        outputs[key] = output.data['text/plain']
    
    return outputs


def main():
    """Main entry point for notebook execution"""
    # First try to get configuration from environment variables
    job_id = os.environ.get('JOB_ID')
    notebook_path_s3 = os.environ.get('NOTEBOOK_PATH')
    parameters_json = os.environ.get('PARAMETERS', '{}')
    requirements_json = os.environ.get('REQUIREMENTS', '{}')
    python_version = os.environ.get('PYTHON_VERSION', '3.10')
    output_dir = os.environ.get('OUTPUT_DIR', '/outputs')
    
    # If any critical variables are missing, fall back to command line args
    if not job_id or not notebook_path_s3:
        args = parse_args()
        
        # Override with command line args if environment variables aren't set
        if not job_id:
            job_id = args.job_id
        if not notebook_path_s3:
            notebook_path_s3 = args.notebook
        if parameters_json == '{}':
            parameters_json = args.parameters
        if requirements_json == '{}':
            requirements_json = args.requirements
        if python_version == '3.10':
            python_version = args.python_version
        output_dir = args.output_dir
    
    # Generate job ID if still not set
    if not job_id:
        job_id = f"job-{uuid.uuid4()}"
        logger.info(f"No job ID provided, generated: {job_id}")
    
    # Parse JSON strings to Python objects
    try:
        parameters = json.loads(parameters_json)
        requirements = json.loads(requirements_json)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {str(e)}")
        sys.exit(1)
    
    try:
        # Report job start
        report_status('running', job_id, {'message': 'Job started'})
        
        # Get S3 configuration
        s3_bucket = os.environ.get('S3_BUCKET')
        if not s3_bucket:
            logger.error("S3_BUCKET environment variable is required")
            sys.exit(1)
        
        # Get S3 client
        s3_client = get_s3_client()
        
        # Prepare paths
        local_notebook_dir = '/notebooks'
        
        # Verify notebook path
        if not notebook_path_s3:
            logger.error("Notebook path must be provided via NOTEBOOK_PATH environment variable or --notebook argument")
            sys.exit(1)
        
        # Download notebook from S3
        notebook_name = os.path.basename(notebook_path_s3)
        local_notebook_path = os.path.join(local_notebook_dir, notebook_name)
        download_notebook_from_s3(s3_client, s3_bucket, notebook_path_s3, local_notebook_path)
        
        # Prepare output paths
        output_dir = Path(output_dir)
        output_notebook = output_dir / f"output_{notebook_name}"
        output_html = output_dir / f"{output_notebook.stem}.html"
        
        # Select Python environment
        kernel_name, python_path = select_python_environment(python_version)
        logger.info(f"Using Python interpreter: {python_path}")
        
        # Install custom requirements
        install_requirements(requirements, python_path)
                
        # Execute notebook (use parameters directly without validation)
        execute_notebook(local_notebook_path, output_notebook, parameters, kernel_name)
        
        # Convert to HTML
        convert_notebook_to_html(output_notebook, output_html)
        
        # Prepare S3 output path
        s3_output_prefix = os.environ.get('S3_OUTPUT_PREFIX', 'outputs')
        
        # Generate output path if not provided
        if os.environ.get('OUTPUT_PATH'):
            s3_output_path = os.environ.get('OUTPUT_PATH')
        else:
            # Use the JOB_ID to construct a path if no OUTPUT_PATH provided
            s3_output_path = f"{s3_output_prefix}/{job_id}"
            logger.info(f"OUTPUT_PATH not set, using: {s3_output_path}")
        
        # Upload notebook output
        output_notebook_s3_key = f"{s3_output_path}/{output_notebook.name}"
        upload_to_s3(s3_client, str(output_notebook), s3_bucket, output_notebook_s3_key)
        
        # Upload HTML output
        output_html_s3_key = f"{s3_output_path}/{output_html.name}"
        upload_to_s3(s3_client, str(output_html), s3_bucket, output_html_s3_key)
        
        # Create result details for API
        result_details = {
            'output_notebook': f"s3://{s3_bucket}/{output_notebook_s3_key}",
            'output_html': f"s3://{s3_bucket}/{output_html_s3_key}",
            'execution_time': time.time(),
            'parameters': parameters,
        }
        
        # Report completion
        report_status('completed', job_id, result_details)
        
        logger.info("Notebook execution completed successfully.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Notebook execution failed: {str(e)}")
        # Report failure
        error_details = {
            'error': str(e),
            'traceback': str(sys.exc_info())
        }
        report_status('failed', job_id, error_details)
        sys.exit(1)

if __name__ == "__main__":
    main() 