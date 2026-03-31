"""Health check and root routes."""

import logging
from fastapi import APIRouter

from models import HealthResponse
from services.gemini_service import check_gemini_health
from services.twilio_service import check_twilio_health
from services.s3_service import check_s3_health
from db.supabase_service import check_supabase_health

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "service": "SwasthaLink API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health",
    }


@router.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check for all services."""
    gemini_health = check_gemini_health()
    twilio_health = check_twilio_health()
    supabase_health = check_supabase_health()
    s3_health = check_s3_health()

    all_ok = all(
        c.get("status") == "ok"
        for c in [gemini_health, twilio_health, supabase_health, s3_health]
    )
    critical_ok = gemini_health.get("status") == "ok"

    if critical_ok and all_ok:
        status = "ok"
    elif critical_ok:
        status = "degraded"
    else:
        status = "down"

    return HealthResponse(
        status=status,
        service="SwasthaLink",
        version="1.0.0",
        checks={
            "gemini": gemini_health,
            "twilio": twilio_health,
            "supabase": supabase_health,
            "s3": s3_health,
        },
    )
