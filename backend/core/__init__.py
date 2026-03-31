"""
Core package — shared configuration, helpers, and exception classes.
"""

from core.config import read_env, FRONTEND_URL, ALLOWED_ORIGINS
from core.exceptions import (
    GeminiServiceError,
    TwilioServiceError,
    S3ServiceError,
    AuthServiceError,
    OTPServiceError,
    SupabaseServiceError,
)

__all__ = [
    "read_env",
    "FRONTEND_URL",
    "ALLOWED_ORIGINS",
    "GeminiServiceError",
    "TwilioServiceError",
    "S3ServiceError",
    "AuthServiceError",
    "OTPServiceError",
    "SupabaseServiceError",
]
