from fastapi import APIRouter, Depends, HTTPException
from app.core.config import get_settings
from app.db.session import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.services.storage.factory import create_storage_service
import boto3
import os
import psutil
import time

settings = get_settings()

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy"}

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with component status"""
    start_time = time.time()
    
    health_status = {
        "status": "healthy",
        "components": {
            "database": {"status": "unknown"},
            "storage": {"status": "unknown"},
            "system": {
                "status": "healthy",
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            }
        },
        "environment": settings.ENV,
        "version": settings.VERSION
    }
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["components"]["database"] = {
            "status": "healthy"
        }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check storage
    try:
        storage = create_storage_service()
        await storage.list_notebooks("")
        health_status["components"]["storage"] = {
            "status": "healthy"
        }
    except Exception as e:
        health_status["components"]["storage"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Add response time
    health_status["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
    
    return health_status

@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check for Kubernetes"""
    try:
        # Check database
        db.execute(text("SELECT 1"))
        
        # Check storage
        storage = create_storage_service()
        await storage.list_notebooks("")
        
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e)) 