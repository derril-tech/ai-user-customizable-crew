"""
Health check router.
"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0")


@router.get("/ready", response_model=HealthResponse)
async def readiness_check():
    """Readiness check endpoint."""
    # TODO: Add database connectivity check
    return HealthResponse(status="ready", version="1.0.0")
