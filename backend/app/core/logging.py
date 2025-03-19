import structlog
import logging
import re
from app.core.config import get_settings

settings = get_settings()

class SensitiveDataFilter(logging.Filter):
    """
    Filter to redact sensitive information in logs
    """
    def __init__(self):
        super().__init__()
        self.patterns = [
            (re.compile(r'password\s*[=:]\s*[\'"]?([^\'",\s]+)[\'"]?', re.IGNORECASE), r'password=*****'),
            (re.compile(r'current_password\s*[=:]\s*[\'"]?([^\'",\s]+)[\'"]?', re.IGNORECASE), r'current_password=*****'),
            (re.compile(r'new_password\s*[=:]\s*[\'"]?([^\'",\s]+)[\'"]?', re.IGNORECASE), r'new_password=*****'),
            (re.compile(r'token\s*[=:]\s*[\'"]?([^\'",\s]+)[\'"]?', re.IGNORECASE), r'token=*****'),
            (re.compile(r'api_key\s*[=:]\s*[\'"]?([^\'",\s]+)[\'"]?', re.IGNORECASE), r'api_key=*****'),
        ]
    
    def filter(self, record):
        if isinstance(record.msg, str):
            msg = record.msg
            for pattern, replacement in self.patterns:
                msg = pattern.sub(replacement, msg)
            record.msg = msg
        return True

def setup_logging():
    """Configure structured logging"""
    # Set up the sensitive data filter
    sensitive_filter = SensitiveDataFilter()
    
    # Configure logging
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Add filter to root logger
    logging.getLogger().addFilter(sensitive_filter)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    # Quiet some chatty loggers
    logging.getLogger("kubernetes").setLevel(logging.WARNING)
    # logging.getLogger("urllib3").setLevel(logging.WARNING)
    # logging.getLogger("boto3").setLevel(logging.WARNING)
    # logging.getLogger("botocore").setLevel(logging.WARNING)
    # logging.getLogger("s3transfer").setLevel(logging.WARNING) 