# FastAPI application entry point
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.middleware import rate_limit_middleware
from app.core.logging import setup_logging
from app.db.session import SessionLocal
from app.db.init_db import init_db
import asyncio
import logging
import os
import uvicorn

load_dotenv()

logger = logging.getLogger(__name__)

settings = get_settings()

# Setup logging
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}

if __name__ == "__main__":
    dev_mode = os.getenv("ENV", "development") == "development"
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=dev_mode)
