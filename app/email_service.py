"""
email_service.py — SMTP email confirmation for booked appointments.

Uses Gmail SMTP with App Passwords.  Gracefully skips sending if
credentials are not configured (logs a warning instead of crashing).
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings
from app.utils import setup_logger

logger = setup_logger("email_service")


def _build_email_body(appointment: dict) -> str:
    """Build an HTML email body with appointment details."""
    return f"""
    <html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; background: #f0f4f8; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: white; border-radius: 12px;
                    padding: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">

            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="color: #0D9488; margin: 0;">🏥 Healthcare AI Assistant</h1>
                <p style="color: #64748b; font-size: 14px;">Appointment Confirmation</p>
            </div>

            <hr style="border: none; border-top: 2px solid #e2e8f0; margin: 20px 0;">

            <h2 style="color: #1e293b;">✅ Appointment Confirmed!</h2>

            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                <tr>
                    <td style="padding: 10px; color: #64748b; font-weight: bold;">Appointment ID</td>
                    <td style="padding: 10px; color: #0D9488; font-weight: bold; font-size: 16px;">
                        {appointment.get('appointment_id', 'N/A')}
                    </td>
                </tr>
                <tr style="background: #f8fafc;">
                    <td style="padding: 10px; color: #64748b; font-weight: bold;">Patient Name</td>
                    <td style="padding: 10px; color: #1e293b;">{appointment.get('patient_name', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; color: #64748b; font-weight: bold;">Age / Gender</td>
                    <td style="padding: 10px; color: #1e293b;">
                        {appointment.get('age', 'N/A')} / {appointment.get('gender', 'N/A')}
                    </td>
                </tr>
                <tr style="background: #f8fafc;">
                    <td style="padding: 10px; color: #64748b; font-weight: bold;">Specialization</td>
                    <td style="padding: 10px; color: #1e293b;">{appointment.get('specialization', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; color: #64748b; font-weight: bold;">Symptoms</td>
                    <td style="padding: 10px; color: #1e293b;">{appointment.get('symptoms', 'N/A')}</td>
                </tr>
                <tr style="background: #f8fafc;">
                    <td style="padding: 10px; color: #64748b; font-weight: bold;">Preferred Date</td>
                    <td style="padding: 10px; color: #1e293b;">{appointment.get('preferred_date', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; color: #64748b; font-weight: bold;">Selected Slot</td>
                    <td style="padding: 10px; color: #0D9488; font-weight: bold;">
                        {appointment.get('slot', 'N/A')}
                    </td>
                </tr>
                <tr style="background: #f8fafc;">
                    <td style="padding: 10px; color: #64748b; font-weight: bold;">Booked At</td>
                    <td style="padding: 10px; color: #1e293b;">
                        {appointment.get('booking_timestamp', 'N/A')}
                    </td>
                </tr>
            </table>

            <hr style="border: none; border-top: 2px solid #e2e8f0; margin: 20px 0;">

            <p style="color: #94a3b8; font-size: 12px; text-align: center;">
                This is an automated confirmation from the Healthcare AI Assistant.<br>
                This assistant is for informational and appointment-support purposes only
                and not a replacement for professional medical advice.
            </p>
        </div>
    </body>
    </html>
    """


def send_confirmation_email(appointment: dict) -> bool:
    """
    Send an appointment confirmation email.

    Parameters
    ----------
    appointment : dict
        Full appointment record.

    Returns
    -------
    bool
        True if sent successfully, False otherwise.
    """
    # Check if credentials are configured
    if not settings.SMTP_EMAIL or not settings.SMTP_PASSWORD:
        logger.warning(
            "SMTP credentials not configured. Skipping email for appointment %s. "
            "Set SMTP_EMAIL and SMTP_PASSWORD in .env to enable.",
            appointment.get("appointment_id", "?"),
        )
        return False

    recipient = appointment.get("email", "")
    if not recipient:
        logger.warning("No recipient email — skipping email send.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = (
            f"✅ Appointment Confirmed — {appointment.get('appointment_id', '')} | "
            f"{appointment.get('specialization', 'Healthcare')}"
        )
        msg["From"] = settings.SMTP_EMAIL
        msg["To"] = recipient

        html_body = _build_email_body(appointment)
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(
            "Confirmation email sent to %s for appointment %s",
            recipient, appointment.get("appointment_id", "?"),
        )
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed. Check SMTP_EMAIL and SMTP_PASSWORD.")
        return False
    except smtplib.SMTPException as exc:
        logger.error("SMTP error: %s", exc)
        return False
    except Exception as exc:
        logger.error("Email sending failed: %s", exc)
        return False
