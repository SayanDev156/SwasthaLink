"""
OTP Service — WhatsApp / SMS OTP via Twilio Verify API.
"""

import logging
from typing import Dict, Any

from core.config import read_env
from core.exceptions import OTPServiceError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Twilio Verify setup
# ---------------------------------------------------------------------------

try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    TWILIO_SDK_AVAILABLE = True
except ImportError:
    Client = None

    class TwilioRestException(Exception):
        """Fallback when Twilio SDK is missing."""

    TWILIO_SDK_AVAILABLE = False


TWILIO_ACCOUNT_SID = read_env("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = read_env("TWILIO_AUTH_TOKEN")
TWILIO_API_KEY_SID = read_env("TWILIO_API_KEY_SID", "TWILIO_API_KEY")
TWILIO_API_KEY_SECRET = read_env("TWILIO_API_KEY_SECRET", "TWILIO_API_SECRET")
TWILIO_VERIFY_SERVICE_SID = read_env("TWILIO_VERIFY_SERVICE_SID")

# Build the Twilio client
_twilio_client = None
if TWILIO_SDK_AVAILABLE:
    if TWILIO_ACCOUNT_SID and TWILIO_API_KEY_SID and TWILIO_API_KEY_SECRET:
        try:
            _twilio_client = Client(TWILIO_API_KEY_SID, TWILIO_API_KEY_SECRET, TWILIO_ACCOUNT_SID)
        except Exception as exc:
            logger.error(f"OTP service: Failed to create Twilio client (API Key): {exc}")
    elif TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        try:
            _twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        except Exception as exc:
            logger.error(f"OTP service: Failed to create Twilio client (Auth Token): {exc}")


# ---------------------------------------------------------------------------
# In-memory OTP fallback (for demo/testing without Twilio Verify)
# ---------------------------------------------------------------------------
_DEMO_OTP_STORE: Dict[str, str] = {}
_DEMO_OTP_CODE = "123456"  # fixed demo code for testing
SUPPORTED_CHANNELS = {"whatsapp", "sms"}


def _normalize_channel(channel: str) -> str:
    normalized = (channel or "").strip().lower()
    if normalized not in SUPPORTED_CHANNELS:
        raise OTPServiceError("OTP channel must be either 'whatsapp' or 'sms'", 400)
    return normalized


def _is_verify_configured() -> bool:
    return bool(_twilio_client and TWILIO_VERIFY_SERVICE_SID)


def _should_fallback_to_demo(exc: Exception) -> bool:
    message = str(exc).lower()
    return (
        "unverified" in message
        or "trial account" in message
        or "phone number is unverified" in message
        or "verify it at twilio.com/user/account/phone-numbers/verified" in message
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def send_otp(phone_number: str, channel: str = "whatsapp") -> Dict[str, Any]:
    """Send an OTP to the given phone number."""
    if not phone_number or not phone_number.startswith("+"):
        raise OTPServiceError("Phone number must be in E.164 format (e.g. +919876543210)", 400)
    normalized_channel = _normalize_channel(channel)

    # --- Real Twilio Verify ---
    if _is_verify_configured():
        try:
            verification = _twilio_client.verify \
                .v2 \
                .services(TWILIO_VERIFY_SERVICE_SID) \
                .verifications \
                .create(to=phone_number, channel=normalized_channel)

            logger.info(f"OTP sent to {phone_number} via {normalized_channel} — SID: {verification.sid}")
            return {
                "success": True,
                "message": f"OTP sent to {phone_number} via {normalized_channel}",
                "demo_mode": False,
                "channel": normalized_channel,
                "phone_number": phone_number,
                "delivery_target": phone_number,
                "configured": True,
            }
        except TwilioRestException as exc:
            logger.error(f"Twilio Verify error: {exc}")
            if _should_fallback_to_demo(exc):
                logger.warning(f"Falling back to demo OTP for {phone_number} after Twilio trial restriction")
                _DEMO_OTP_STORE[phone_number] = _DEMO_OTP_CODE
                return {
                    "success": True,
                    "message": (
                        f"Demo OTP ({_DEMO_OTP_CODE}) assigned for {phone_number} via {normalized_channel}. "
                        "Twilio trial accounts can only send to verified numbers."
                    ),
                    "demo_mode": True,
                    "fallback_reason": "twilio_trial_unverified_number",
                    "channel": normalized_channel,
                    "phone_number": phone_number,
                    "delivery_target": phone_number,
                    "configured": True,
                }
            raise OTPServiceError(f"Failed to send OTP: {exc.msg}", 502)
        except Exception as exc:
            logger.error(f"Unexpected OTP send error: {exc}")
            raise OTPServiceError(f"Failed to send OTP: {str(exc)}", 500)

    # --- Demo fallback ---
    logger.warning(f"Twilio Verify not configured — using demo OTP for {phone_number}")
    _DEMO_OTP_STORE[phone_number] = _DEMO_OTP_CODE
    return {
        "success": True,
        "message": f"Demo OTP ({_DEMO_OTP_CODE}) assigned for {phone_number} via {normalized_channel}",
        "demo_mode": True,
        "channel": normalized_channel,
        "phone_number": phone_number,
        "delivery_target": phone_number,
        "configured": False,
    }


async def verify_otp(phone_number: str, code: str) -> Dict[str, Any]:
    """Verify a previously sent OTP."""
    if not phone_number or not phone_number.startswith("+"):
        raise OTPServiceError("Phone number must be in E.164 format", 400)
    if not code or len(code) < 4:
        raise OTPServiceError("OTP code is required (minimum 4 digits)", 400)

    # If we issued a demo OTP for this number, verify against the local store first.
    expected = _DEMO_OTP_STORE.get(phone_number)
    if expected is not None:
        verified = code == expected
        if verified:
            del _DEMO_OTP_STORE[phone_number]

        return {
            "success": True,
            "verified": verified,
            "status": "approved" if verified else "pending",
            "demo_mode": True,
        }

    # --- Real Twilio Verify ---
    if _is_verify_configured():
        try:
            verification_check = _twilio_client.verify \
                .v2 \
                .services(TWILIO_VERIFY_SERVICE_SID) \
                .verification_checks \
                .create(to=phone_number, code=code)

            approved = verification_check.status == "approved"
            logger.info(f"OTP verification for {phone_number}: {verification_check.status}")
            return {
                "success": True,
                "verified": approved,
                "status": verification_check.status,
                "demo_mode": False,
            }
        except TwilioRestException as exc:
            logger.error(f"Twilio Verify check error: {exc}")
            return {
                "success": False,
                "verified": False,
                "error": str(exc.msg),
                "demo_mode": False,
            }
        except Exception as exc:
            logger.error(f"Unexpected OTP verify error: {exc}")
            raise OTPServiceError(f"OTP verification failed: {str(exc)}", 500)

    return {
        "success": False,
        "verified": False,
        "error": "No OTP was sent for this number. Send OTP first.",
        "demo_mode": False,
    }
