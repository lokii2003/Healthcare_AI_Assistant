"""
models.py — Pydantic request / response schemas for the FastAPI backend.
"""

from pydantic import BaseModel, Field


# ── Chat ────────────────────────────────────────────────────────────────────

class QuestionRequest(BaseModel):
    """Payload for the /ask endpoint."""
    question: str = Field(..., min_length=1, description="User question text")


class AnswerResponse(BaseModel):
    """Response from the /ask endpoint."""
    answer: str
    sources: list[str] = []
    intent: str = "rag"          # "rag" or "appointment"


# ── Appointments ────────────────────────────────────────────────────────────

class AppointmentRequest(BaseModel):
    """Payload for the /book-appointment endpoint."""
    patient_name: str = Field(..., min_length=1)
    age: int = Field(..., ge=0, le=150)
    gender: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    symptoms: str = ""
    specialization: str = Field(..., min_length=1)
    preferred_date: str = Field(..., min_length=1)
    slot: str = Field(..., min_length=1)


class AppointmentResponse(BaseModel):
    """Confirmation response after booking."""
    status: str = "success"
    appointment_id: str
    patient_name: str
    specialization: str
    slot: str
    preferred_date: str
    booking_timestamp: str
    message: str = "Appointment booked successfully!"


# ── Ingestion ───────────────────────────────────────────────────────────────

class IngestResponse(BaseModel):
    """Response from the /ingest endpoint."""
    status: str
    message: str
    txt_files_created: int = 0
    chunks_indexed: int = 0
