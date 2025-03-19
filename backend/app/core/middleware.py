from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from time import time
from collections import defaultdict
import logging
from typing import Dict, List, Callable, Awaitable, Tuple
import asyncio
from contextlib import asynccontextmanager

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Rate limiting configuration
CLIENT_RATE_LIMIT = 5000  # requests per client
RATE_WINDOW = 3600  # seconds (1 hour)

# Global rate limits for specific endpoint+method combinations
# Format: (path, method): limit
GLOBAL_ENDPOINT_LIMITS: Dict[Tuple[str, str], int] = {
    ("/api/v1/executions", "POST"): settings.GLOBAL_EXECUTIONS_RATE_LIMIT,  # POST requests to executions per hour globally
}

# Storage for rate limit tracking
client_requests = defaultdict(list)  # Per-client tracking
endpoint_requests = defaultdict(list)  # Per-endpoint global tracking
endpoint_locks = defaultdict(asyncio.Lock)  # Locks to prevent race conditions

@asynccontextmanager
async def safe_execution():
    """Context manager to safely handle exceptions in middleware"""
    try:
        yield
    except Exception as e:
        logger.exception(f"Error in middleware: {str(e)}")
        # Re-raise only if it's an HTTPException, otherwise convert to 500
        if isinstance(e, HTTPException):
            raise
        else:
            raise HTTPException(status_code=500, detail="Internal server error")

async def rate_limit_middleware(request: Request, call_next):
    """
    Enhanced rate limiting middleware with:
    1. Per-client rate limiting
    2. Global rate limiting for specific endpoint+method combinations
    3. Improved error handling
    """
    client = request.client.host if request.client else "unknown"
    path = request.url.path
    method = request.method
    now = time()
    
    try:
        # 1. Apply client-specific rate limiting
        async with asyncio.Lock():
            # Clean old requests
            client_requests[client] = [
                req_time for req_time in client_requests[client] 
                if now - req_time < RATE_WINDOW
            ]
            
            # Check if client exceeds their limit
            if len(client_requests[client]) >= CLIENT_RATE_LIMIT:
                logger.warning(f"Rate limit exceeded for client {client}")
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please try again later."}
                )
            
            # Track this request
            client_requests[client].append(now)
        
        # 2. Apply global rate limiting for specific endpoint+method combinations
        endpoint_key = (path, method)
        if endpoint_key in GLOBAL_ENDPOINT_LIMITS:
            endpoint_limit = GLOBAL_ENDPOINT_LIMITS[endpoint_key]
            
            # Use a lock specific to this endpoint+method to prevent race conditions
            lock_key = f"{path}:{method}"
            async with endpoint_locks[lock_key]:
                # Clean old requests for this endpoint+method
                endpoint_requests[lock_key] = [
                    req_time for req_time in endpoint_requests[lock_key]
                    if now - req_time < RATE_WINDOW
                ]
                
                # Check if global limit for this endpoint+method is exceeded
                if len(endpoint_requests[lock_key]) >= endpoint_limit:
                    logger.warning(f"Global rate limit exceeded for {method} {path}")
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "This endpoint is currently rate-limited. Please try again later."}
                    )
                
                # Track this request against the endpoint+method limit
                endpoint_requests[lock_key].append(now)
        
        # 3. Process the request
        return await call_next(request)
    
    except HTTPException as e:
        # Properly handle FastAPI HTTP exceptions
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail}
        )
    except Exception as e:
        # Log any other exceptions and return a 500 error
        logger.exception(f"Error in middleware: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        ) 