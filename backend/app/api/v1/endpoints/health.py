from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "bug-bounty-platform-api",
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint
    """
    # TODO: Add database connection check
    # TODO: Add Redis connection check
    
    return {
        "status": "ready",
        "database": "connected",
        "redis": "connected"
    } 