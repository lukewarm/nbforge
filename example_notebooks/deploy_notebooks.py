#!/usr/bin/env python3
"""
Notebook Deployment Script

This script copies Jupyter notebooks to an S3 bucket based on environment settings.
It can be used for manual deployment or as part of a CI/CD pipeline.

Usage:
    python deploy_notebooks.py [--notebooks PATTERN] [--env ENV_FILE]

Examples:
    # Deploy all notebooks
    python deploy_notebooks.py
    
    # Deploy specific notebooks
    python deploy_notebooks.py --notebooks "customer_*.ipynb"
    
    # Use a specific env file
    python deploy_notebooks.py --env ../backend/.env.production
"""

import os
import sys
import glob
import argparse
import logging
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('notebook-deployer')

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Deploy notebooks to S3 bucket')
    parser.add_argument('--notebooks', default='*.ipynb', 
                        help='Pattern to match notebook files (default: *.ipynb)')
    parser.add_argument('--env', default='../backend/.env',
                        help='Environment file to load (default: backend/.env)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be uploaded without actually uploading')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    return parser.parse_args()

def load_environment(env_file):
    """Load environment variables from file."""
    env_path = Path(env_file)
    if not env_path.exists():
        logger.warning(f"Environment file {env_file} not found. Checking for .env")
        env_path = Path('.env')
        if not env_path.exists():
            logger.warning(f"Default .env file not found. Checking for .env.example")
            env_path = Path('.env.example')
            if not env_path.exists():
                logger.error("No environment file found. Please create .env file.")
                sys.exit(1)
    
    logger.info(f"Loading environment from {env_path}")
    load_dotenv(dotenv_path=env_path)
    
    # Check for required environment variables
    required_vars = ['S3_BUCKET', 'S3_ENDPOINT_URL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file")
        sys.exit(1)

def get_s3_client():
    """Create and configure S3 client based on environment variables."""
    endpoint_url = os.getenv('S3_ENDPOINT_URL')
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    # Configure S3 client
    s3_config = {
        'aws_access_key_id': aws_access_key,
        'aws_secret_access_key': aws_secret_key,
    }
    
    # Add endpoint URL for MinIO or custom S3 endpoints
    if endpoint_url:
        s3_config['endpoint_url'] = endpoint_url
        
    try:
        s3_client = boto3.client('s3', **s3_config)
        return s3_client
    except Exception as e:
        logger.error(f"Failed to create S3 client: {str(e)}")
        sys.exit(1)

def upload_notebook(s3_client, notebook_path, bucket, prefix='notebooks'):
    """Upload a notebook to S3 bucket."""
    try:
        # Get the notebook filename
        notebook_name = os.path.basename(notebook_path)
        
        # Construct the S3 key (path in the bucket)
        s3_key = f"{prefix}/{notebook_name}"
        
        logger.info(f"Uploading {notebook_path} to s3://{bucket}/{s3_key}")
        
        # Upload the file
        with open(notebook_path, 'rb') as file:
            s3_client.upload_fileobj(
                file,
                bucket,
                s3_key,
                ExtraArgs={'ContentType': 'application/json'}
            )
        
        logger.info(f"Successfully uploaded {notebook_name}")
        return True
    except ClientError as e:
        logger.error(f"Error uploading {notebook_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error uploading {notebook_path}: {e}")
        return False

def main():
    """Main function to deploy notebooks to S3."""
    args = parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Load environment variables
    load_environment(args.env)
    
    # Get S3 configuration
    bucket_name = os.getenv('S3_BUCKET')
    prefix = os.getenv('S3_NOTEBOOK_TEMPLATES_PREFIX', 'notebooks')
    
    logger.info(f"Deploying notebooks to bucket: {bucket_name}, prefix: {prefix}")
    
    # Find notebooks matching the pattern
    notebook_pattern = args.notebooks
    notebooks = glob.glob(notebook_pattern)
    
    if not notebooks:
        logger.warning(f"No notebooks found matching pattern: {notebook_pattern}")
        return
    
    logger.info(f"Found {len(notebooks)} notebooks to deploy")
    
    if args.dry_run:
        logger.info("DRY RUN: Would upload the following notebooks:")
        for notebook in notebooks:
            logger.info(f"  - {notebook} -> s3://{bucket_name}/{prefix}/{os.path.basename(notebook)}")
        return
    
    # Get S3 client
    s3_client = get_s3_client()
    
    # Upload each notebook
    success_count = 0
    for notebook in notebooks:
        if upload_notebook(s3_client, notebook, bucket_name, prefix):
            success_count += 1
    
    logger.info(f"Deployment complete: {success_count}/{len(notebooks)} notebooks uploaded successfully")

if __name__ == "__main__":
    main() 