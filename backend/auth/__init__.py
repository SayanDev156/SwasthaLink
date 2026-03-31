"""
Auth package — login, signup, OTP services.
"""

from auth.auth_service import login_user, signup_patient
from core.exceptions import AuthServiceError

__all__ = ["login_user", "signup_patient", "AuthServiceError"]
