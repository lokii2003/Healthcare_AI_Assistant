"""
main.py — FastAPI application entry-point for the Healthcare AI Assistant.

The frontend is served separately via Streamlit (streamlit run frontend/streamlit_app.py).
Swagger docs remain at /docs for developer use.

Endpoints
─────────
GET  /health              Health-check / liveness probe
POST /ingest              Convert XML → TXT and ingest into ChromaDB
POST /ask                 Route question through AI agent (RAG or Appointment)
POST /book-appointment    Book an appointment (SQLite + email)
GET  /appointments        List all appointments
GET  /appointments/stats  Dashboard statistics
POST /reset               Clear conversation history
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import (
    QuestionRequest, AnswerResponse,
    AppointmentRequest, AppointmentResponse,
    IngestResponse,
)
from app.database import init_db, save_appointment, get_all_appointments, get_appointment_stats
from app.email_service import send_confirmation_email
from app.utils import setup_logger

logger = setup_logger("main")


# ── Lifespan (startup / shutdown) ──────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup."""
    logger.info("Starting Healthcare AI Assistant…")
    init_db()
    logger.info("Database initialized.")
    yield
    logger.info("Shutting down Healthcare AI Assistant.")


# ── FastAPI app ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="Healthcare AI Assistant",
    description="RAG-powered healthcare assistant with appointment booking, "
                "ChromaDB vector search, and Ollama Mistral LLM.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the Streamlit frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory conversation history (single-user demo mode)
conversation_history: list[dict] = []


# ── API Endpoints ──────────────────────────────────────────────────────────

@app.get("/health", tags=["Utility"])
async def health_check():
    """Return API status and metadata."""
    return {
        "status": "healthy",
        "service": "Healthcare AI Assistant",
        "llm_model": settings.OLLAMA_MODEL,
        "ollama_url": settings.OLLAMA_BASE_URL,
    }


@app.post("/ingest", response_model=IngestResponse, tags=["RAG"])
async def ingest_documents():
    """
    1. Convert all XML files in /data to TXT in /txt_data
    2. Ingest TXT files into ChromaDB vector store
    """
    try:
        from app.xml_converter import convert_all_xml_to_txt
        from app.embeddings import ingest_all_documents

        # Step 1: XML → TXT
        logger.info("Starting XML → TXT conversion…")
        txt_count = convert_all_xml_to_txt()

        # Step 2: TXT → ChromaDB
        logger.info("Starting document ingestion into ChromaDB…")
        chunk_count = ingest_all_documents()

        logger.info("Ingestion complete — %d TXT files, %d chunks indexed.", txt_count, chunk_count)
        return IngestResponse(
            status="success",
            message=f"Converted {txt_count} XML files and indexed {chunk_count} chunks.",
            txt_files_created=txt_count,
            chunks_indexed=chunk_count,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Ingestion failed.")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/ask", response_model=AnswerResponse, tags=["Chat"])
async def ask_question(payload: QuestionRequest):
    """
    Accept a user question, route through the AI agent, return an answer.

    The agent decides:
      • Healthcare knowledge → RAG pipeline
      • Appointment booking  → Appointment agent
    """
    global conversation_history

    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        from app.agent import route_question

        result = route_question(question, conversation_history)

        # Track conversation
        conversation_history.append({"role": "user", "content": question})
        conversation_history.append({"role": "assistant", "content": result["answer"]})

        # Keep history manageable (last 20 turns = 40 messages)
        if len(conversation_history) > 40:
            conversation_history = conversation_history[-40:]

        return AnswerResponse(
            answer=result["answer"],
            sources=result.get("sources", []),
            intent=result.get("intent", "rag"),
        )

    except Exception as exc:
        logger.exception("Error processing question.")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/book-appointment", response_model=AppointmentResponse, tags=["Appointments"])
async def book_appointment(payload: AppointmentRequest):
    """Validate, store appointment in SQLite, and send confirmation email."""
    try:
        data = payload.model_dump()

        # Save to database
        record = save_appointment(data)
        logger.info("Appointment booked: %s", record["appointment_id"])

        # Send email (non-blocking — failure won't break the booking)
        email_sent = send_confirmation_email(record)
        if email_sent:
            record["message"] = "Appointment booked and confirmation email sent!"
        else:
            record["message"] = "Appointment booked successfully! (Email not configured)"

        return AppointmentResponse(**record)

    except Exception as exc:
        logger.exception("Appointment booking failed.")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/appointments", tags=["Appointments"])
async def list_appointments():
    """Return all appointments from SQLite."""
    try:
        appointments = get_all_appointments()
        return {"appointments": appointments, "total": len(appointments)}
    except Exception as exc:
        logger.exception("Failed to fetch appointments.")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/appointments/stats", tags=["Appointments"])
async def appointment_stats():
    """Return aggregate appointment statistics for the dashboard."""
    try:
        stats = get_appointment_stats()
        return stats
    except Exception as exc:
        logger.exception("Failed to fetch stats.")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/reset", tags=["Utility"])
async def reset_conversation():
    """Clear conversation history."""
    global conversation_history
    conversation_history = []
    return {"status": "conversation reset"}


# ── Development runner ──────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )
