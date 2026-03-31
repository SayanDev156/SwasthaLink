"""
Pydantic models for the prescription RAG pipeline.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class PrescriptionMedication(BaseModel):
    """Single medication extracted from a handwritten prescription"""
    name: str = Field(..., description="Drug name (generic preferred)")
    strength: Optional[str] = Field(None, description="e.g. '500mg', '5ml'")
    form: Optional[str] = Field(None, description="Tab / Cap / Syrup / Inj / Drops etc.")
    frequency: Optional[str] = Field(None, description="e.g. 'OD', 'BD', 'TDS', 'QID'")
    duration: Optional[str] = Field(None, description="e.g. '5 days', '2 weeks'")
    instructions: Optional[str] = Field(None, description="e.g. 'After food', 'At bedtime'")


class PrescriptionExtractedData(BaseModel):
    """All fields extracted from a handwritten prescription via RAG pipeline"""
    doctor_name: Optional[str] = Field(None, description="Prescribing doctor's full name")
    patient_id: Optional[str] = Field(None, description="UHID / MRN / Patient ID")
    patient_name: Optional[str] = Field(None, description="Patient's full name")
    patient_age: Optional[str] = Field(None, description="Age string, e.g. '35 yrs' or '35/M'")
    patient_gender: Optional[str] = Field(None, description="Male / Female / Other")
    prescription_date: Optional[str] = Field(None, description="Date on prescription")
    medications: List[PrescriptionMedication] = Field(
        default_factory=list, description="List of prescribed medications"
    )
    diagnosis: Optional[str] = Field(None, description="Diagnosis or presenting complaint")
    notes: Optional[str] = Field(None, description="Additional instructions or notes")
    extraction_confidence: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Overall OCR/extraction confidence score"
    )


class PrescriptionStatusEnum(str, Enum):
    """Lifecycle status of a prescription record"""
    PENDING = "pending_admin_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class PrescriptionRecord(BaseModel):
    """Full prescription workflow record stored in the backend"""
    prescription_id: str = Field(..., description="Unique UUID for this prescription")
    status: PrescriptionStatusEnum = Field(
        default=PrescriptionStatusEnum.PENDING, description="Current workflow status"
    )
    doctor_id: str = Field(..., description="ID of the uploading doctor")
    extracted_data: PrescriptionExtractedData = Field(
        ..., description="RAG-extracted prescription fields"
    )
    s3_key: Optional[str] = Field(None, description="S3 object key of the original file")
    created_at: str = Field(..., description="ISO-8601 creation timestamp")
    admin_id: Optional[str] = Field(None, description="Admin who reviewed the record")
    reviewed_at: Optional[str] = Field(None, description="ISO-8601 review timestamp")
    rejection_reason: Optional[str] = Field(None, description="Reason if rejected")


class PrescriptionExtractResponse(BaseModel):
    """Response returned after prescription extraction + record creation"""
    prescription_id: str
    status: str
    extracted_data: PrescriptionExtractedData
    message: str = "Prescription submitted for admin review"


class PrescriptionApproveRequest(BaseModel):
    """Admin approval request"""
    admin_id: str = Field(..., description="ID of the approving admin")


class PrescriptionRejectRequest(BaseModel):
    """Admin rejection request"""
    admin_id: str = Field(..., description="ID of the rejecting admin")
    reason: str = Field(..., min_length=5, description="Reason for rejection")


class PrescriptionPatientViewResponse(BaseModel):
    """Patient-facing readable view of an approved prescription"""
    prescription_id: str
    doctor_name: str = Field(default="Your doctor")
    patient_name: str = Field(default="Patient")
    patient_age: Optional[str] = None
    prescription_date: Optional[str] = None
    diagnosis: Optional[str] = None
    medications: List[PrescriptionMedication]
    notes: Optional[str] = None
    approved_at: Optional[str] = None
