import logging
import sys
import os
from typing import Optional

def setup_logging(level: Optional[str] = None) -> None:
    """Configure logging for the application"""
    if level is None:
        level = "DEBUG" if os.getenv("DEBUG") else "INFO"

    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('notebook_runner.log')
        ]
    )

    # Configure specific loggers
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('papermill').setLevel(logging.INFO)
    
    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info("Notebook Runner starting up")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Log level: {level}") 