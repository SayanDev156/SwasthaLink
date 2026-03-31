"""Prescription RAG pipeline routes."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from models import (
    PrescriptionExtractResponse, PrescriptionApproveRequest,
    PrescriptionRejectRequest, PrescriptionPatientViewResponse,
)
from services.gemini_service import extract_text_from_image
from services.s3_service import upload_file
from services.rate_alert_service import rate_alert_service
from services.prescription_rag_service import (
    extract_prescription_data, create_prescription_record,
    list_pending_records, approve_record, reject_record,
    get_record, get_approved_record,
    list_records_by_doctor, list_approved_for_patient,
)
from core.exceptions import GeminiServiceError, S3ServiceError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/prescriptions/by-doctor/{doctor_id}")
async def get_prescriptions_by_doctor(doctor_id: str):
    """Return all prescriptions uploaded by a specific doctor."""
    try:
        records = await list_records_by_doctor(doctor_id)
        return {"count": len(records), "items": [r.model_dump() for r in records]}
    except Exception as exc:
        logger.error(f"Error fetching doctor prescriptions: {exc}")
        raise HTTPException(status_code=500, detail="Failed to fetch prescriptions")


@router.get("/api/prescriptions/for-patient/{patient_id}")
async def get_prescriptions_for_patient(patient_id: str):
    """Return all approved prescriptions for a patient."""
    try:
        records = await list_approved_for_patient(patient_id)
        return {"count": len(records), "items": [r.model_dump() for r in records]}
    except Exception as exc:
        logger.error(f"Error fetching patient prescriptions: {exc}")
        raise HTTPException(status_code=500, detail="Failed to fetch prescriptions")


@router.post("/api/prescriptions/extract", response_model=PrescriptionExtractResponse)
async def extract_prescription(file: UploadFile = File(...), doctor_id: str = Form(...)):
    """Extract structured information from a handwritten prescription."""
    try:
        allowed_types = ["application/pdf", "image/jpeg", "image/png", "image/jpg"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}. Allowed: PDF, JPG, PNG")
        if not doctor_id or not doctor_id.strip():
            raise HTTPException(status_code=400, detail="doctor_id is required")

        logger.info(f"Prescription upload by doctor {doctor_id}: {file.filename}")
        file_content = await file.read()

        s3_key: Optional[str] = None
        try:
            s3_result = await upload_file(file_content=file_content, filename=file.filename,
                                          session_id=f"rx_{doctor_id}", content_type=file.content_type)
            s3_key = s3_result.get("s3_key")
            rate_alert_service.track_usage("s3", context="/api/prescriptions/extract")
        except S3ServiceError as exc:
            logger.warning(f"S3 upload failed (non-critical): {exc}")

        ocr_text = await extract_text_from_image(image_data=file_content, mime_type=file.content_type)
        rate_alert_service.track_usage("gemini", context="ocr:/api/prescriptions/extract")

        extracted_data = await extract_prescription_data(ocr_text)
        rate_alert_service.track_usage("gemini", context="rag:/api/prescriptions/extract")

        record = await create_prescription_record(extracted_data=extracted_data, doctor_id=doctor_id.strip(), s3_key=s3_key)
        logger.info(f"Prescription record created: {record.prescription_id}")

        return PrescriptionExtractResponse(
            prescription_id=record.prescription_id, status=record.status.value, extracted_data=record.extracted_data,
        )
    except GeminiServiceError as exc:
        logger.error(f"Gemini error during prescription extraction: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected error during prescription extraction: {exc}")
        raise HTTPException(status_code=500, detail=f"Prescription extraction failed: {str(exc)}")


@router.get("/api/prescriptions/pending")
async def get_pending_prescriptions():
    """List all prescriptions awaiting admin review."""
    try:
        records = await list_pending_records()
        return {"count": len(records), "items": [r.model_dump() for r in records]}
    except Exception as exc:
        logger.error(f"Error fetching pending prescriptions: {exc}")
        raise HTTPException(status_code=500, detail="Failed to fetch pending prescriptions")


@router.post("/api/prescriptions/{prescription_id}/approve")
async def approve_prescription(prescription_id: str, request: PrescriptionApproveRequest):
    """Admin approves a pending prescription."""
    try:
        record = await approve_record(prescription_id, request.admin_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"Prescription {prescription_id} not found")
        logger.info(f"Prescription {prescription_id} approved by admin {request.admin_id}")
        return {"prescription_id": record.prescription_id, "status": record.status.value,
                "reviewed_at": record.reviewed_at, "message": "Prescription approved and delivered to patient"}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error approving prescription {prescription_id}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to approve prescription")


@router.post("/api/prescriptions/{prescription_id}/reject")
async def reject_prescription(prescription_id: str, request: PrescriptionRejectRequest):
    """Admin rejects a pending prescription with a reason."""
    try:
        record = await reject_record(prescription_id, request.admin_id, request.reason)
        if record is None:
            raise HTTPException(status_code=404, detail=f"Prescription {prescription_id} not found")
        logger.info(f"Prescription {prescription_id} rejected by admin {request.admin_id}")
        return {"prescription_id": record.prescription_id, "status": record.status.value,
                "reviewed_at": record.reviewed_at, "rejection_reason": record.rejection_reason,
                "message": "Prescription rejected"}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error rejecting prescription {prescription_id}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to reject prescription")


@router.get("/api/prescriptions/{prescription_id}/patient-view", response_model=PrescriptionPatientViewResponse)
async def get_patient_prescription_view(prescription_id: str):
    """Return an approved prescription in patient-readable format."""
    try:
        raw = await get_record(prescription_id)
        if raw is None:
            raise HTTPException(status_code=404, detail="Prescription not found")
        if raw.status.value == "pending_admin_review":
            raise HTTPException(status_code=403, detail="Prescription is awaiting admin approval")
        if raw.status.value == "rejected":
            raise HTTPException(status_code=403, detail="Prescription was rejected by admin")

        record = await get_approved_record(prescription_id)
        if record is None:
            raise HTTPException(status_code=403, detail="Prescription is not approved")

        data = record.extracted_data
        return PrescriptionPatientViewResponse(
            prescription_id=record.prescription_id,
            doctor_name=data.doctor_name or "Your doctor",
            patient_name=data.patient_name or "Patient",
            patient_age=data.patient_age,
            prescription_date=data.prescription_date,
            diagnosis=data.diagnosis,
            medications=data.medications,
            notes=data.notes,
            approved_at=record.reviewed_at,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error fetching patient view for {prescription_id}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to retrieve prescription")
