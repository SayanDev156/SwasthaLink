"""
Database package — Supabase client, session/prescription/profile CRUD.
"""

from db.supabase_service import (
    supabase_client,
    log_session,
    persist_session_history,
    append_session_event,
    get_session_history,
    list_recent_histories,
    update_session_quiz_score,
    update_session_whatsapp_status,
    get_session_count,
    get_analytics,
    generate_session_id,
    check_supabase_health,
)

from db.prescription_db import (
    create_prescription,
    list_pending_prescriptions,
    list_prescriptions_by_doctor,
    list_approved_prescriptions_for_patient,
    approve_prescription_db,
    reject_prescription_db,
    get_prescription_by_id,
)

from db.profile_db import (
    create_patient_profile,
    update_phone_verified,
    list_patients,
)

__all__ = [
    "supabase_client",
    "log_session", "persist_session_history", "append_session_event",
    "get_session_history", "list_recent_histories",
    "update_session_quiz_score", "update_session_whatsapp_status",
    "get_session_count", "get_analytics",
    "generate_session_id", "check_supabase_health",
    "create_prescription", "list_pending_prescriptions",
    "list_prescriptions_by_doctor", "list_approved_prescriptions_for_patient",
    "approve_prescription_db", "reject_prescription_db", "get_prescription_by_id",
    "create_patient_profile", "update_phone_verified", "list_patients",
]
