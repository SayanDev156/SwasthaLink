"""
AI package — prompt templates and generation configuration.
"""

from ai.prompts import (
    format_master_prompt,
    format_re_explain_prompt,
    format_ocr_prompt,
    GENERATION_CONFIG,
    SAFETY_SETTINGS,
    SYSTEM_INSTRUCTION,
    ROLE_INSTRUCTIONS,
    BENGALI_VALIDATION_PROMPT,
    MEDICATION_EXTRACTION_PROMPT,
)

__all__ = [
    "format_master_prompt",
    "format_re_explain_prompt",
    "format_ocr_prompt",
    "GENERATION_CONFIG",
    "SAFETY_SETTINGS",
    "SYSTEM_INSTRUCTION",
    "ROLE_INSTRUCTIONS",
    "BENGALI_VALIDATION_PROMPT",
    "MEDICATION_EXTRACTION_PROMPT",
]
