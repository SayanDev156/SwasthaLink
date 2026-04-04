"""
Twilio WhatsApp Service
Handles all WhatsApp message sending via Twilio API
Supports both sandbox (development) and production WhatsApp Business API
"""

import logging
from typing import Dict, Any

try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    TWILIO_SDK_AVAILABLE = True
except ImportError:
    Client = None

    class TwilioRestException(Exception):
        """Fallback exception when Twilio SDK is not installed."""

    TWILIO_SDK_AVAILABLE = False

from core.config import read_env
from core.exceptions import TwilioServiceError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not TWILIO_SDK_AVAILABLE:
    logger.warning("Twilio SDK not installed. Install with: pip install twilio")

# Load Twilio credentials from environment
TWILIO_ACCOUNT_SID = read_env("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = read_env("TWILIO_AUTH_TOKEN")
TWILIO_API_KEY_SID = read_env("TWILIO_API_KEY_SID", "TWILIO_API_KEY")
TWILIO_API_KEY_SECRET = read_env("TWILIO_API_KEY_SECRET", "TWILIO_API_SECRET")
TWILIO_WHATSAPP_NUMBER = read_env("TWILIO_WHATSAPP_NUMBER") or "whatsapp:+14155238886"

# Initialize Twilio client
twilio_client = None
TWILIO_AUTH_MODE = "unconfigured"
if not TWILIO_SDK_AVAILABLE:
    logger.warning("Twilio client disabled because Twilio SDK is unavailable")
elif TWILIO_ACCOUNT_SID and TWILIO_API_KEY_SID and TWILIO_API_KEY_SECRET:
    try:
        twilio_client = Client(TWILIO_API_KEY_SID, TWILIO_API_KEY_SECRET, TWILIO_ACCOUNT_SID)
        TWILIO_AUTH_MODE = "api_key"
        logger.info("Twilio client initialized successfully using API Key authentication")
    except Exception as e:
        logger.error(f"Failed to initialize Twilio client with API Key: {e}")
elif TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        TWILIO_AUTH_MODE = "auth_token"
        logger.info("Twilio client initialized successfully using Account SID/Auth Token")
    except Exception as e:
        logger.error(f"Failed to initialize Twilio client: {e}")
else:
    logger.warning(
        "Twilio credentials not found. Set either "
        "(TWILIO_ACCOUNT_SID + TWILIO_API_KEY_SID + TWILIO_API_KEY_SECRET) "
        "or (TWILIO_ACCOUNT_SID + TWILIO_AUTH_TOKEN)."
    )


def _format_phone_number(phone: str) -> str:
    """Ensure phone number is in WhatsApp format."""
    if phone.startswith("whatsapp:"):
        return phone
    return f"whatsapp:{phone}"


def _truncate_message(message: str, max_length: int = 1600) -> str:
    """Truncate message if it exceeds WhatsApp limits."""
    if len(message) <= max_length:
        return message
    truncated = message[:max_length - 50]
    truncated += "\n\n...(message truncated)\n\n_Full details in your discharge papers_"
    logger.warning(f"Message truncated from {len(message)} to {len(truncated)} characters")
    return truncated


async def send_whatsapp_message(phone_number: str, message: str) -> Dict[str, Any]:
    """Send WhatsApp message via Twilio."""
    try:
        if not TWILIO_SDK_AVAILABLE:
            raise TwilioServiceError(
                "Twilio SDK is not installed. Run `pip install twilio` or install from requirements.txt."
            )

        if not twilio_client:
            raise TwilioServiceError(
                "Twilio client not initialized. Check either "
                "(TWILIO_ACCOUNT_SID + TWILIO_API_KEY_SID + TWILIO_API_KEY_SECRET) "
                "or (TWILIO_ACCOUNT_SID + TWILIO_AUTH_TOKEN)."
            )

        from_number = _format_phone_number(TWILIO_WHATSAPP_NUMBER)
        to_number = _format_phone_number(phone_number)
        message = _truncate_message(message)

        logger.info(f"Sending WhatsApp message to {phone_number}")
        logger.info(f"Message length: {len(message)} characters")

        twilio_message = twilio_client.messages.create(
            from_=from_number,
            to=to_number,
            body=message
        )

        logger.info(f"WhatsApp message sent successfully. SID: {twilio_message.sid}")
        logger.info(f"Status: {twilio_message.status}")

        return {
            "success": True,
            "sid": twilio_message.sid,
            "status": twilio_message.status,
            "to": phone_number,
            "from": TWILIO_WHATSAPP_NUMBER
        }

    except TwilioRestException as e:
        error_code = e.code
        error_msg = e.msg
        logger.error(f"Twilio API error {error_code}: {error_msg}")

        error_mappings = {
            21211: "Invalid 'To' phone number. Please check the format (+country_code + number).",
            21408: "Recipient not joined Twilio sandbox. Ask them to send 'join <code>' to the sandbox number.",
            21610: "Recipient has unsubscribed from messages. They need to rejoin.",
            63007: "Recipient phone number not capable of receiving WhatsApp messages.",
            63016: "Message failed due to rate limit or spam filter."
        }

        user_friendly_msg = error_mappings.get(
            error_code,
            f"WhatsApp delivery failed: {error_msg}"
        )

        return {
            "success": False,
            "sid": None,
            "status": "failed",
            "error": user_friendly_msg,
            "error_code": error_code
        }

    except Exception as e:
        logger.error(f"Unexpected error sending WhatsApp message: {e}")
        logger.exception(e)

        return {
            "success": False,
            "sid": None,
            "status": "failed",
            "error": f"Failed to send WhatsApp message: {str(e)}"
        }


async def send_bulk_whatsapp_messages(recipients: list[Dict[str, str]]) -> Dict[str, Any]:
    """Send WhatsApp messages to multiple recipients (Post-MVP feature)."""
    results = []
    successful = 0
    failed = 0

    for recipient in recipients:
        phone = recipient.get("phone_number")
        msg = recipient.get("message")

        if not phone or not msg:
            logger.warning(f"Skipping invalid recipient: {recipient}")
            failed += 1
            results.append({
                "phone_number": phone,
                "success": False,
                "error": "Missing phone_number or message"
            })
            continue

        result = await send_whatsapp_message(phone, msg)
        results.append({"phone_number": phone, **result})

        if result["success"]:
            successful += 1
        else:
            failed += 1

    logger.info(f"Bulk send complete: {successful} successful, {failed} failed out of {len(recipients)}")

    return {
        "total": len(recipients),
        "successful": successful,
        "failed": failed,
        "results": results
    }


def get_message_status(message_sid: str) -> Dict[str, Any]:
    """Check status of a previously sent message."""
    try:
        if not TWILIO_SDK_AVAILABLE:
            raise TwilioServiceError("Twilio SDK is not installed")

        if not twilio_client:
            raise TwilioServiceError("Twilio client not initialized")

        message = twilio_client.messages(message_sid).fetch()

        return {
            "success": True,
            "sid": message.sid,
            "status": message.status,
            "error_code": message.error_code,
            "error_message": message.error_message,
            "date_sent": message.date_sent.isoformat() if message.date_sent else None,
            "date_updated": message.date_updated.isoformat() if message.date_updated else None,
        }

    except TwilioRestException as e:
        logger.error(f"Failed to fetch message status: {e}")
        return {"success": False, "error": str(e)}


def check_twilio_health() -> Dict[str, Any]:
    """Check if Twilio service is accessible and healthy."""
    try:
        if not TWILIO_SDK_AVAILABLE:
            return {"status": "down", "message": "Twilio SDK package not installed", "available": False}

        if not twilio_client:
            return {"status": "down", "message": "Twilio client not initialized. Check credentials.", "available": False}

        if TWILIO_AUTH_MODE == "api_key":
            return {
                "status": "ok",
                "message": "Twilio client initialized (API key mode)",
                "available": True,
                "auth_mode": TWILIO_AUTH_MODE,
            }

        account = twilio_client.api.accounts(TWILIO_ACCOUNT_SID).fetch()

        if account.status == "active":
            return {
                "status": "ok",
                "message": "Twilio service is healthy",
                "available": True,
                "account_status": account.status,
                "auth_mode": TWILIO_AUTH_MODE,
            }
        else:
            return {
                "status": "degraded",
                "message": f"Twilio account status: {account.status}",
                "available": False,
                "account_status": account.status,
                "auth_mode": TWILIO_AUTH_MODE,
            }

    except Exception as e:
        logger.error(f"Twilio health check failed: {e}")
        return {"status": "down", "message": str(e), "available": False}


def format_whatsapp_message(
    condition: str,
    medications: list[str],
    follow_up: str,
    emergency_signs: list[str]
) -> str:
    """Helper function to format WhatsApp message with consistent structure."""
    message = f"*SwasthaLink* 🏥\n\n{condition}\n\n"

    if medications:
        message += "*💊 Your key medicines:*\n"
        for med in medications[:3]:
            message += f"• {med}\n"
        message += "\n"

    if follow_up:
        message += f"*📅 See doctor:* {follow_up}\n\n"

    if emergency_signs:
        message += "*🚨 Go to emergency if:*\n"
        message += " · ".join(emergency_signs[:3])
        message += "\n\n"

    message += "_Powered by SwasthaLink · ownworldmade_"
    return message


def get_sandbox_instructions() -> str:
    """Get instructions for joining Twilio WhatsApp sandbox."""
    return f"""
    📱 **Join Twilio WhatsApp Sandbox:**

    1. Save this number in your contacts: {TWILIO_WHATSAPP_NUMBER.replace('whatsapp:', '')}
    2. Send a WhatsApp message: "join <your-sandbox-code>"
    3. You'll receive a confirmation message
    4. You can now receive messages from SwasthaLink!

    Note: Sandbox connections expire after 72 hours of inactivity.
    Rejoin by sending "join <code>" again.

    **For production:** Use Twilio WhatsApp Business API with proper number verification.
    """
