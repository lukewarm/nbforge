from . import auth, notebooks, executions, health, service_accounts, users, static
from fastapi import APIRouter

__all__ = ["notebooks", "executions", "health", "service_accounts", "users", "static"]

api_router = APIRouter()
api_router.include_router(notebooks.router, tags=["notebooks"])
api_router.include_router(executions.router, tags=["executions"])
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"], prefix="/auth")
api_router.include_router(service_accounts.router, tags=["service-accounts"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(static.router, tags=["static"]) 