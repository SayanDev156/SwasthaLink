"""
Pydantic models for WhatsApp messaging.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal


class WhatsAppRequest(BaseModel):
    """Request model for /api/send-whatsapp endpoint"""
    phone_number: str = Field(..., pattern=r'^\+\d{10,15}$', description="E.164 format: +919876543210")
    message: str = Field(..., min_length=10, max_length=1600, description="Message content")
    session_id: Optional[str] = Field(None, description="Session tracking ID for persistent timeline")

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        if not v.startswith('+'):
            raise ValueError('Phone number must start with + and country code')
        return v


class WhatsAppResponse(BaseModel):
    """Response model for WhatsApp send operation"""
    status: Literal["sent", "failed"]
    message: str
    sid: Optional[str] = Field(None, description="Twilio message SID if successful")
