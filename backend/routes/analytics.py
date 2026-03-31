"""Analytics, sessions, and patient directory routes."""

import logging
from fastapi import APIRouter, HTTPException

from db.supabase_service import (
    get_analytics, get_session_history, list_recent_histories, get_session_count,
)
from db.profile_db import list_patients
from services.rate_alert_service import rate_alert_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/analytics")
async def get_analytics_data():
    """Get aggregated analytics data."""
    try:
        return await get_analytics()
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")


@router.get("/api/rate-alerts/status")
async def get_rate_alert_status():
    """Get current rate usage counters and threshold status."""
    return rate_alert_service.get_status()


@router.get("/api/sessions/{session_id}/history")
async def get_persisted_session_history(session_id: str):
    """Get full persisted history for a session."""
    history = await get_session_history(session_id)
    if not history.get("success"):
        raise HTTPException(status_code=404, detail=history.get("error", "Session history not found"))
    return history


@router.get("/api/sessions/history/recent")
async def get_recent_session_histories(limit: int = 20):
    """List recent persisted session histories."""
    safe_limit = min(max(limit, 1), 100)
    data = await list_recent_histories(safe_limit)
    return {"count": len(data), "items": data}


@router.get("/api/sessions/count")
async def get_sessions_count():
    """Get total number of sessions processed."""
    try:
        count = await get_session_count()
        return {"total_sessions": count}
    except Exception as e:
        logger.error(f"Error fetching session count: {e}")
        return {"total_sessions": 0}


@router.get("/api/patients")
async def get_patients():
    """Return patient profiles for doctor-facing dropdowns."""
    try:
        patients = await list_patients()
        return {"count": len(patients), "items": patients}
    except Exception as exc:
        logger.error(f"Error fetching patients: {exc}")
        raise HTTPException(status_code=500, detail="Failed to fetch patients")
