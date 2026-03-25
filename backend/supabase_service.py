"""
Supabase Service
Handles session logging + persistent history storage.

By default this service stores full session history so user context is not lost.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from supabase import create_client, Client
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase_client: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
else:
    logger.warning("Supabase credentials not found in environment variables")


class SupabaseServiceError(Exception):
    """Custom exception for Supabase service errors"""
    pass


def _history_enabled() -> bool:
    """Feature flag for full persistent history storage."""
    return os.getenv("STORE_FULL_HISTORY", "true").strip().lower() == "true"


def generate_session_id() -> str:
    """
    Generate unique session ID

    Returns:
        UUID string
    """
    return str(uuid.uuid4())


async def log_session(
    role: str,
    language: str,
    quiz_score: Optional[int] = None,
    whatsapp_sent: bool = False,
    re_explained: bool = False,
    log_format: str = "text",
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Log session metadata to Supabase

    Args:
        role: User role ('patient', 'caregiver', 'elderly')
        language: Output language ('en', 'bn', 'both')
        quiz_score: Comprehension quiz score (0-3)
        whatsapp_sent: Whether message was sent to WhatsApp
        re_explained: Whether content was re-explained for low quiz score
        log_format: Input format ('text', 'pdf', 'image')
        session_id: Optional session ID (generated if not provided)

    Returns:
        Dict with session info including session_id

    """
    try:
        if not supabase_client:
            logger.warning("Supabase client not available - skipping session logging")
            return {
                "success": False,
                "session_id": session_id or generate_session_id(),
                "error": "Supabase not configured"
            }

        # Generate session ID if not provided
        if not session_id:
            session_id = generate_session_id()

        # Prepare session metadata
        session_data = {
            "id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "role": role,
            "language": language,
            "quiz_score": quiz_score,
            "whatsapp_sent": whatsapp_sent,
            "re_explained": re_explained,
            "log_format": log_format
        }

        # Insert into Supabase
        result = supabase_client.table("sessions").insert(session_data).execute()

        logger.info(f"Session logged successfully: {session_id}")

        return {
            "success": True,
            "session_id": session_id,
            "data": result.data[0] if result.data else session_data
        }

    except Exception as e:
        logger.error(f"Failed to log session: {e}")
        # Don't raise - session logging failure shouldn't break the main flow
        return {
            "success": False,
            "session_id": session_id or generate_session_id(),
            "error": str(e)
        }


async def persist_session_history(
    session_id: str,
    role: str,
    language: str,
    discharge_text: str,
    process_response: Dict[str, Any],
    re_explain: bool = False,
) -> Dict[str, Any]:
    """
    Persist full clinical request + AI response for long-term history continuity.
    """
    try:
        if not _history_enabled():
            return {"success": False, "session_id": session_id, "error": "History storage disabled"}

        if not supabase_client:
            logger.warning("Supabase client not available")
            return {"success": False, "session_id": session_id, "error": "Supabase not configured"}

        payload = {
            "session_id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "role": role,
            "language": language,
            "discharge_text": discharge_text,
            "simplified_english": process_response.get("simplified_english"),
            "simplified_bengali": process_response.get("simplified_bengali"),
            "medications": process_response.get("medications", []),
            "follow_up": process_response.get("follow_up"),
            "warning_signs": process_response.get("warning_signs", []),
            "comprehension_questions": process_response.get("comprehension_questions", []),
            "whatsapp_message": process_response.get("whatsapp_message"),
            "re_explain": re_explain,
        }

        result = supabase_client.table("session_history").insert(payload).execute()
        return {
            "success": True,
            "session_id": session_id,
            "data": result.data[0] if result.data else payload,
        }
    except Exception as e:
        logger.error(f"Failed to persist session history: {e}")
        return {"success": False, "session_id": session_id, "error": str(e)}


async def append_session_event(
    session_id: str,
    event_type: str,
    event_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Append timeline events (quiz, whatsapp, etc.) for historical traceability.
    """
    try:
        if not _history_enabled():
            return {"success": False, "session_id": session_id, "error": "History storage disabled"}

        if not supabase_client:
            return {"success": False, "session_id": session_id, "error": "Supabase not configured"}

        payload = {
            "session_id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "event_data": event_data or {},
        }

        result = supabase_client.table("session_events").insert(payload).execute()
        return {
            "success": True,
            "session_id": session_id,
            "data": result.data[0] if result.data else payload,
        }
    except Exception as e:
        logger.error(f"Failed to append session event: {e}")
        return {"success": False, "session_id": session_id, "error": str(e)}


async def get_session_history(session_id: str) -> Dict[str, Any]:
    """
    Fetch full persisted history and events for a specific session.
    """
    try:
        if not supabase_client:
            return {"success": False, "session_id": session_id, "error": "Supabase not configured"}

        history_result = (
            supabase_client
            .table("session_history")
            .select("*")
            .eq("session_id", session_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        events_result = (
            supabase_client
            .table("session_events")
            .select("*")
            .eq("session_id", session_id)
            .order("created_at", desc=False)
            .execute()
        )

        return {
            "success": True,
            "session_id": session_id,
            "history": history_result.data[0] if history_result.data else None,
            "events": events_result.data or [],
        }
    except Exception as e:
        logger.error(f"Failed to fetch session history: {e}")
        return {"success": False, "session_id": session_id, "error": str(e)}


async def list_recent_histories(limit: int = 20) -> List[Dict[str, Any]]:
    """
    List recent persisted histories for admin/recovery workflows.
    """
    try:
        if not supabase_client:
            return []

        result = (
            supabase_client
            .table("session_history")
            .select("session_id, created_at, role, language")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception as e:
        logger.error(f"Failed to list recent histories: {e}")
        return []


async def update_session_quiz_score(session_id: str, quiz_score: int, re_explained: bool = False) -> Dict[str, Any]:
    """
    Update session with quiz score after quiz submission

    Args:
        session_id: Session ID
        quiz_score: Quiz score (0-3)
        re_explained: Whether content was re-explained

    Returns:
        Dict with update status
    """
    try:
        if not supabase_client:
            logger.warning("Supabase client not available")
            return {"success": False, "error": "Supabase not configured"}

        # Update session
        result = supabase_client.table("sessions").update({
            "quiz_score": quiz_score,
            "re_explained": re_explained
        }).eq("id", session_id).execute()

        logger.info(f"Session {session_id} updated with quiz score: {quiz_score}")

        return {
            "success": True,
            "session_id": session_id,
            "quiz_score": quiz_score
        }

    except Exception as e:
        logger.error(f"Failed to update session quiz score: {e}")
        return {
            "success": False,
            "session_id": session_id,
            "error": str(e)
        }


async def update_session_whatsapp_status(session_id: str, whatsapp_sent: bool) -> Dict[str, Any]:
    """
    Update session with WhatsApp delivery status

    Args:
        session_id: Session ID
        whatsapp_sent: Whether message was successfully sent

    Returns:
        Dict with update status
    """
    try:
        if not supabase_client:
            logger.warning("Supabase client not available")
            return {"success": False, "error": "Supabase not configured"}

        # Update session
        result = supabase_client.table("sessions").update({
            "whatsapp_sent": whatsapp_sent
        }).eq("id", session_id).execute()

        logger.info(f"Session {session_id} updated with WhatsApp status: {whatsapp_sent}")

        return {
            "success": True,
            "session_id": session_id,
            "whatsapp_sent": whatsapp_sent
        }

    except Exception as e:
        logger.error(f"Failed to update WhatsApp status: {e}")
        return {
            "success": False,
            "session_id": session_id,
            "error": str(e)
        }


async def get_session_count() -> int:
    """
    Get total number of sessions processed

    Returns:
        Total session count
    """
    try:
        if not supabase_client:
            return 0

        result = supabase_client.table("sessions").select("id", count="exact").execute()

        count = result.count if hasattr(result, 'count') else len(result.data)
        logger.info(f"Total sessions: {count}")

        return count

    except Exception as e:
        logger.error(f"Failed to get session count: {e}")
        return 0


async def get_analytics() -> Dict[str, Any]:
    """
    Get aggregated analytics (Post-MVP feature)

    Returns:
        Dict with analytics data
    """
    try:
        if not supabase_client:
            return {"error": "Supabase not configured"}

        # Get total sessions
        total_result = supabase_client.table("sessions").select("id", count="exact").execute()
        total = total_result.count if hasattr(total_result, 'count') else len(total_result.data)

        # Get all sessions for analysis
        sessions_result = supabase_client.table("sessions").select("*").execute()
        sessions = sessions_result.data

        # Calculate analytics
        by_role = {"patient": 0, "caregiver": 0, "elderly": 0}
        by_language = {"en": 0, "bn": 0, "both": 0}
        whatsapp_count = 0
        re_explained_count = 0
        avg_quiz_score = 0
        quiz_scores = []

        for session in sessions:
            # Count by role
            role = session.get("role")
            if role in by_role:
                by_role[role] += 1

            # Count by language
            language = session.get("language")
            if language in by_language:
                by_language[language] += 1

            # Count WhatsApp sent
            if session.get("whatsapp_sent"):
                whatsapp_count += 1

            # Count re-explained
            if session.get("re_explained"):
                re_explained_count += 1

            # Collect quiz scores
            score = session.get("quiz_score")
            if score is not None:
                quiz_scores.append(score)

        # Calculate average quiz score
        if quiz_scores:
            avg_quiz_score = sum(quiz_scores) / len(quiz_scores)

        analytics = {
            "total_sessions": total,
            "by_role": by_role,
            "by_language": by_language,
            "whatsapp_sent_count": whatsapp_count,
            "whatsapp_sent_percentage": round((whatsapp_count / total * 100) if total > 0 else 0, 2),
            "re_explained_count": re_explained_count,
            "re_explained_percentage": round((re_explained_count / total * 100) if total > 0 else 0, 2),
            "average_quiz_score": round(avg_quiz_score, 2),
            "quiz_scores_distribution": {
                "0": quiz_scores.count(0),
                "1": quiz_scores.count(1),
                "2": quiz_scores.count(2),
                "3": quiz_scores.count(3)
            }
        }

        logger.info("Analytics calculated successfully")
        return analytics

    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        return {"error": str(e)}


def check_supabase_health() -> Dict[str, Any]:
    """
    Check if Supabase service is accessible and healthy

    Returns:
        Dict with status information
    """
    try:
        if not supabase_client:
            return {
                "status": "down",
                "message": "Supabase client not initialized. Check credentials.",
                "available": False
            }

        # Try to query sessions table
        result = supabase_client.table("sessions").select("id").limit(1).execute()

        return {
            "status": "ok",
            "message": "Supabase service is healthy",
            "available": True,
            "table_accessible": True
        }

    except Exception as e:
        logger.error(f"Supabase health check failed: {e}")
        return {
            "status": "down",
            "message": str(e),
            "available": False
        }


# SQL schema for Supabase table creation (documentation)
SUPABASE_SCHEMA = """
-- Create sessions table for session metadata logging
CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  role TEXT CHECK (role IN ('patient', 'caregiver', 'elderly')),
  language TEXT CHECK (language IN ('en', 'bn', 'both')),
  quiz_score INTEGER CHECK (quiz_score BETWEEN 0 AND 3),
  whatsapp_sent BOOLEAN DEFAULT FALSE,
  re_explained BOOLEAN DEFAULT FALSE,
  log_format TEXT CHECK (log_format IN ('text', 'pdf', 'image')) DEFAULT 'text'
);

-- Create index on created_at for analytics queries
CREATE INDEX idx_sessions_created_at ON sessions(created_at DESC);

-- Create index on role for analytics
CREATE INDEX idx_sessions_role ON sessions(role);

-- Enable Row Level Security (RLS)
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

-- Create policy for anon access (public read/write)
-- Adjust based on your security requirements
CREATE POLICY "Allow all access for development" ON sessions
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Persistent full-history table
CREATE TABLE IF NOT EXISTS session_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    role TEXT,
    language TEXT,
    discharge_text TEXT,
    simplified_english TEXT,
    simplified_bengali TEXT,
    medications JSONB DEFAULT '[]'::jsonb,
    follow_up JSONB,
    warning_signs JSONB DEFAULT '[]'::jsonb,
    comprehension_questions JSONB DEFAULT '[]'::jsonb,
    whatsapp_message TEXT,
    re_explain BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_session_history_session_id ON session_history(session_id);
CREATE INDEX IF NOT EXISTS idx_session_history_created_at ON session_history(created_at DESC);

ALTER TABLE session_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all access for development history" ON session_history
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Session timeline events table
CREATE TABLE IF NOT EXISTS session_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    event_type TEXT NOT NULL,
    event_data JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_session_events_session_id ON session_events(session_id);
CREATE INDEX IF NOT EXISTS idx_session_events_created_at ON session_events(created_at DESC);

ALTER TABLE session_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all access for development events" ON session_events
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- For production, restrict access appropriately
"""


def get_schema_sql() -> str:
    """
    Get SQL schema for creating Supabase tables

    Returns:
        SQL schema string
    """
    return SUPABASE_SCHEMA
