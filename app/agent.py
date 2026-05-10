"""
agent.py — Intelligent routing between RAG and Appointment workflows.

Detects user intent and routes to the appropriate handler:
  • Healthcare knowledge questions → RAG pipeline
  • Appointment booking requests  → Appointment agent
"""

import re
from app.rag import ask_rag
from app.utils import setup_logger

logger = setup_logger("agent")

# ── Intent detection keywords ───────────────────────────────────────────────
APPOINTMENT_KEYWORDS = [
    "book", "appointment", "schedule", "slot", "doctor",
    "booking", "reserve", "visit", "consultation", "consult",
    "available", "timing", "when can i see",
]

# ── Symptom → Specialization mapping ───────────────────────────────────────
SYMPTOM_SPECIALIZATION_MAP = {
    "Dermatologist": [
        "skin", "rash", "allergy", "acne", "eczema", "psoriasis",
        "dermatitis", "hives", "itching", "fungal",
    ],
    "Cardiologist": [
        "chest pain", "heart", "cardiac", "palpitation", "blood pressure",
        "hypertension", "cholesterol", "cardiovascular",
    ],
    "Neurologist": [
        "headache", "migraine", "brain", "seizure", "nerve",
        "numbness", "dizziness", "vertigo", "memory loss", "tremor",
    ],
    "Orthopedic": [
        "bone", "joint", "fracture", "back pain", "knee", "spine",
        "arthritis", "shoulder", "muscle pain", "sprain",
    ],
    "Ophthalmologist": [
        "eye", "vision", "blur", "cataract", "glaucoma",
        "retina", "spectacles", "blindness",
    ],
    "Dentist": [
        "teeth", "tooth", "dental", "gum", "cavity", "braces",
        "wisdom tooth", "oral",
    ],
    "Gastroenterologist": [
        "stomach", "digestion", "acid reflux", "gastric", "liver",
        "nausea", "vomiting", "diarrhea", "constipation", "abdomen",
    ],
    "Pulmonologist": [
        "lung", "breathing", "asthma", "cough", "bronchitis",
        "pneumonia", "respiratory", "wheezing",
    ],
    "ENT Specialist": [
        "ear", "nose", "throat", "sinus", "tonsil", "hearing",
        "snoring", "voice",
    ],
    "General Physician": [
        "fever", "cold", "flu", "fatigue", "weakness", "infection",
        "general", "checkup", "routine",
    ],
}

# ── Mock available slots ────────────────────────────────────────────────────
AVAILABLE_SLOTS = {
    "Cardiologist": ["Monday 10:00 AM", "Monday 2:00 PM", "Wednesday 11:00 AM", "Friday 9:00 AM"],
    "Dermatologist": ["Tuesday 11:00 AM", "Tuesday 3:00 PM", "Thursday 10:00 AM"],
    "Neurologist": ["Monday 9:00 AM", "Wednesday 2:00 PM", "Friday 11:00 AM"],
    "Orthopedic": ["Tuesday 9:00 AM", "Thursday 2:00 PM", "Saturday 10:00 AM"],
    "Ophthalmologist": ["Monday 11:00 AM", "Wednesday 3:00 PM", "Friday 10:00 AM"],
    "Dentist": ["Tuesday 10:00 AM", "Thursday 11:00 AM", "Saturday 9:00 AM"],
    "Gastroenterologist": ["Monday 3:00 PM", "Wednesday 10:00 AM", "Friday 2:00 PM"],
    "Pulmonologist": ["Tuesday 2:00 PM", "Thursday 9:00 AM", "Saturday 11:00 AM"],
    "ENT Specialist": ["Monday 2:00 PM", "Wednesday 9:00 AM", "Friday 3:00 PM"],
    "General Physician": ["Daily 9:00 AM", "Daily 11:00 AM", "Daily 2:00 PM", "Daily 4:00 PM"],
}


def _detect_intent(question: str) -> str:
    """
    Determine if the question is about appointment booking or healthcare knowledge.

    Returns
    -------
    str
        "appointment" or "rag"
    """
    q_lower = question.lower()
    for keyword in APPOINTMENT_KEYWORDS:
        if keyword in q_lower:
            return "appointment"
    return "rag"


def _detect_specialization(text: str) -> str | None:
    """Detect the best-matching specialization from user text."""
    t_lower = text.lower()
    best_match = None
    best_score = 0

    for spec, symptoms in SYMPTOM_SPECIALIZATION_MAP.items():
        score = sum(1 for s in symptoms if s in t_lower)
        if score > best_score:
            best_score = score
            best_match = spec

    return best_match


def _handle_appointment(question: str, history: list[dict]) -> dict:
    """
    Handle appointment-related queries:
    - Detect specialization from symptoms
    - Suggest available slots
    - Guide user to the booking form
    """
    specialization = _detect_specialization(question)

    if specialization:
        slots = AVAILABLE_SLOTS.get(specialization, [])
        slots_text = "\n".join(f"  • {s}" for s in slots) if slots else "  • No slots configured"

        answer = (
            f"Based on your symptoms, I recommend seeing a **{specialization}**.\n\n"
            f"📅 **Available Slots:**\n{slots_text}\n\n"
            f"Please use the **Book Appointment** page to complete your booking. "
            f"Select '{specialization}' as your specialization and choose your preferred slot.\n\n"
            f"_This assistant is for informational and appointment-support purposes only "
            f"and not a replacement for professional medical advice._"
        )
    else:
        # List all specializations
        all_specs = "\n".join(f"  • {s}" for s in AVAILABLE_SLOTS.keys())
        answer = (
            "I'd be happy to help you book an appointment! 🏥\n\n"
            f"**Available Specializations:**\n{all_specs}\n\n"
            "Please tell me your symptoms so I can recommend the right specialist, "
            "or go directly to the **Book Appointment** page to choose your specialization.\n\n"
            "_This assistant is for informational and appointment-support purposes only "
            "and not a replacement for professional medical advice._"
        )

    return {
        "answer": answer,
        "sources": [],
        "intent": "appointment",
        "specialization": specialization,
        "slots": AVAILABLE_SLOTS.get(specialization, []) if specialization else [],
    }


def route_question(question: str, history: list[dict] | None = None) -> dict:
    """
    Route user question to the appropriate handler.

    Parameters
    ----------
    question : str
        User's input.
    history : list[dict], optional
        Conversation history for multi-turn context.

    Returns
    -------
    dict
        {"answer": str, "sources": list[str], "intent": str}
    """
    history = history or []
    intent = _detect_intent(question)
    logger.info("Detected intent '%s' for question: %.60s", intent, question)

    if intent == "appointment":
        return _handle_appointment(question, history)

    # Default: healthcare RAG
    result = ask_rag(question)
    result["intent"] = "rag"
    return result
