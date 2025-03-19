from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict, List
from functools import lru_cache
from pydantic import field_validator

class Settings(BaseSettings):
    """Application settings"""
    
    # Project info
    PROJECT_NAME: str = "NBForge"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Notebook execution platform"
    
    # Environment
    ENV: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"  # Logging level (DEBUG, INFO, WARNING, ERROR)
    
    # API settings
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:8080", "http://127.0.0.1:8080"]
    
    # Database settings
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/nbforge"
    
    # Storage settings
    S3_BUCKET: str = "nbforge"
    S3_ENDPOINT_URL: Optional[str] = None  # For local development with MinIO
    S3_NOTEBOOK_TEMPLATES_PREFIX: str = "notebooks"  # Prefix for notebook templates in S3
    
    # Kubernetes settings
    K8S_NAMESPACE: str = "default"
    NOTEBOOK_RUNNER_IMAGE: str = "nbforge/notebook-runner:latest"
    
    # API URL for callbacks
    API_URL: str = "http://localhost:8000/api/v1"
    
    # Execution settings
    DEFAULT_PYTHON_VERSION: str = "3.10"
    DEFAULT_CPU_MILLI: int = 1000
    DEFAULT_MEMORY_MIB: int = 2048
    GLOBAL_EXECUTIONS_RATE_LIMIT: int = 100
        
    # Security
    SECRET_KEY: str = "your-secret-key-for-development"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # Default to 7 days
    
    # API configuration
    API_VERSION: str = "v1"
     
    # AWS settings
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    
    # JWT Settings
    ALGORITHM: str = "HS256"
    
    # OAuth Settings
    OAUTH_PROVIDERS: Dict = {
        "google": {
            "client_id": "",
            "client_secret": "",
        },
        "github": {
            "client_id": "",
            "client_secret": "",
        }
    }
    
    # Auth Demo Mode
    DEMO_MODE: bool = False
    DEMO_USER: str = "demo@nbforge.com"
    
    # Email settings
    EMAILS_ENABLED: bool = False
    EMAIL_PROVIDER: str = "dummy"  # "smtp" or "dummy"
    EMAIL_FROM: str = "noreply@example.com"
    EMAIL_FROM_NAME: str = "NBForge"

    # SMTP settings
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True

    # Frontend URL for links in emails
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Fix for CORS_ORIGINS to handle string values from environment
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value
    
    # Handle boolean environment variables like DEMO_MODE
    @field_validator("DEMO_MODE", "EMAILS_ENABLED", "SMTP_TLS", mode="before")
    @classmethod 
    def parse_bool(cls, value):
        if isinstance(value, str):
            return value.lower() == "true"
        return value
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
