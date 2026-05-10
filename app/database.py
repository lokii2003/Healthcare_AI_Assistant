"""
database.py — SQLite appointment database.

Manages the appointments table: creation, insertion, and querying.
"""

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.config import DB_PATH
from app.utils import setup_logger

logger = setup_logger("database")


def _get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the appointments table if it does not exist."""
    conn = _get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id   TEXT PRIMARY KEY,
                patient_name     TEXT NOT NULL,
                age              INTEGER NOT NULL,
                gender           TEXT NOT NULL,
                email            TEXT NOT NULL,
                phone            TEXT NOT NULL,
                symptoms         TEXT,
                specialization   TEXT NOT NULL,
                preferred_date   TEXT NOT NULL,
                slot             TEXT NOT NULL,
                booking_timestamp TEXT NOT NULL
            )
        """)
        conn.commit()
        logger.info("Database initialized at %s", DB_PATH)
    except sqlite3.Error as exc:
        logger.error("Database initialization failed: %s", exc)
        raise
    finally:
        conn.close()


def save_appointment(data: dict) -> dict:
    """
    Insert a new appointment into the database.

    Parameters
    ----------
    data : dict
        Appointment details (patient_name, age, gender, email, phone,
        symptoms, specialization, preferred_date, slot).

    Returns
    -------
    dict
        Full appointment record including generated appointment_id and timestamp.
    """
    appointment_id = f"APT-{uuid.uuid4().hex[:8].upper()}"
    booking_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    conn = _get_connection()
    try:
        conn.execute(
            """
            INSERT INTO appointments
                (appointment_id, patient_name, age, gender, email, phone,
                 symptoms, specialization, preferred_date, slot, booking_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                appointment_id,
                data["patient_name"],
                data["age"],
                data["gender"],
                data["email"],
                data["phone"],
                data.get("symptoms", ""),
                data["specialization"],
                data["preferred_date"],
                data["slot"],
                booking_timestamp,
            ),
        )
        conn.commit()
        logger.info("Appointment saved: %s for %s", appointment_id, data["patient_name"])
    except sqlite3.Error as exc:
        logger.error("Failed to save appointment: %s", exc)
        raise
    finally:
        conn.close()

    return {
        "appointment_id": appointment_id,
        "patient_name": data["patient_name"],
        "age": data["age"],
        "gender": data["gender"],
        "email": data["email"],
        "phone": data["phone"],
        "symptoms": data.get("symptoms", ""),
        "specialization": data["specialization"],
        "preferred_date": data["preferred_date"],
        "slot": data["slot"],
        "booking_timestamp": booking_timestamp,
    }


def get_all_appointments() -> list[dict]:
    """Return all appointments ordered by most recent first."""
    conn = _get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM appointments ORDER BY booking_timestamp DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        logger.error("Failed to fetch appointments: %s", exc)
        return []
    finally:
        conn.close()


def get_appointment_stats() -> dict:
    """
    Return aggregate appointment statistics for the admin dashboard.

    Returns
    -------
    dict
        total, by_specialization (dict), recent (list of last 5)
    """
    conn = _get_connection()
    try:
        # Total count
        total = conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]

        # By specialization
        rows = conn.execute(
            "SELECT specialization, COUNT(*) as count FROM appointments GROUP BY specialization ORDER BY count DESC"
        ).fetchall()
        by_specialization = {row["specialization"]: row["count"] for row in rows}

        # Recent 5
        recent_rows = conn.execute(
            "SELECT * FROM appointments ORDER BY booking_timestamp DESC LIMIT 5"
        ).fetchall()
        recent = [dict(r) for r in recent_rows]

        return {
            "total": total,
            "by_specialization": by_specialization,
            "recent": recent,
        }
    except sqlite3.Error as exc:
        logger.error("Failed to fetch stats: %s", exc)
        return {"total": 0, "by_specialization": {}, "recent": []}
    finally:
        conn.close()
