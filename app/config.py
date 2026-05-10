"""
config.py — Centralised configuration for the Healthcare AI Assistant.

All settings are loaded from environment variables (with sensible defaults)
via pydantic-settings.  Create a `.env` file in the project root to override.
"""

from pathlib import Path
from pydantic_settings import BaseSettings


# ── Path constants ──────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent          # project root
DATA_DIR = BASE_DIR / "data"                                # XML source files
TXT_DATA_DIR = BASE_DIR / "txt_data"                        # converted TXT files
VECTOR_STORE_DIR = BASE_DIR / "vector_store"                # ChromaDB persistence
LOGS_DIR = BASE_DIR / "logs"                                # application logs
FRONTEND_DIR = BASE_DIR / "frontend"                        # HTML/CSS/JS frontend
DB_PATH = BASE_DIR / "appointments.db"                      # SQLite database


class Settings(BaseSettings):
    """
    Application-wide settings.
    Values are read from a `.env` file or OS environment variables.
    """

    # ── LLM / Ollama ────────────────────────────────────────────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"

    # ── Embeddings ──────────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ── RAG Tuning ──────────────────────────────────────────────────────────
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RETRIEVER_K: int = 4                          # top-k docs to retrieve

    # ── Email / SMTP ────────────────────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_EMAIL: str = ""
    SMTP_PASSWORD: str = ""

    # ── Server ──────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"


# Singleton instance — import this everywhere
settings = Settings()

# Ensure required directories exist on import
for _dir in (DATA_DIR, TXT_DATA_DIR, VECTOR_STORE_DIR, LOGS_DIR, FRONTEND_DIR):
    _dir.mkdir(parents=True, exist_ok=True)
