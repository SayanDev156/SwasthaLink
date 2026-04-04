"""
User profile CRUD helpers — extracted from supabase_service.py.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def _get_client():
    """Lazy import to avoid circular dependencies."""
    from db.supabase_service import supabase_client
    return supabase_client


async def create_patient_profile(
    user_id: str,
    name: str,
    email: str,
    phone: str,
    role: str = "patient",
) -> Dict[str, Any]:
    """Insert a row into the profiles table for a new patient."""
    try:
        client = _get_client()
        if not client:
            return {"success": False, "error": "Supabase not configured"}

        profile_data = {
            "user_id": user_id,
            "full_name": name,
            "email": email.strip().lower(),
            "role": role,
            "phone": phone,
            "phone_verified": False,
        }

        result = client.table("profiles").insert(profile_data).execute()
        logger.info(f"Patient profile created for {email}")
        return {"success": True, "data": result.data[0] if result.data else profile_data}
    except Exception as e:
        logger.error(f"Failed to create patient profile: {e}")
        return {"success": False, "error": str(e)}


async def update_phone_verified(user_id: str, phone: str) -> Dict[str, Any]:
    """Mark a phone number as verified in the profiles table."""
    try:
        client = _get_client()
        if not client:
            return {"success": False, "error": "Supabase not configured"}

        client.table("profiles").update({"phone_verified": True}).eq("phone", phone).execute()
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to update phone_verified for {phone}: {e}")
        return {"success": False, "error": str(e)}


async def list_patients() -> List[Dict[str, Any]]:
    """Return all profiles with role=patient."""
    try:
        client = _get_client()
        if not client:
            return []
        result = (
            client
            .table("profiles")
            .select("user_id, full_name, name, email, phone, phone_verified")
            .eq("role", "patient")
            .order("full_name")
            .execute()
        )
        return result.data or []
    except Exception as e:
        logger.error(f"Failed to list patients: {e}")
        return []
