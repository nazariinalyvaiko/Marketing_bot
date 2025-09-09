from __future__ import annotations

import os
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage as SmtpEmailMessage

from dotenv import load_dotenv

from marketing_bot.config import settings
from marketing_bot.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False


@dataclass
class EmailMessage:
    subject: str
    body: str
    to: str
    from_name: str | None = None
    from_email: str | None = None


def send_email(msg: EmailMessage) -> None:
    """Send email via SendGrid (preferred) or SMTP fallback. If SENDER_DRY_RUN, log."""
    dry_run = (
        settings.SENDER_DRY_RUN or os.getenv("SENDER_DRY_RUN", "true").lower() == "true"
    )
    from_name = msg.from_name or settings.EMAIL_SENDER_NAME
    from_email = msg.from_email or settings.EMAIL_SENDER_ADDR

    if dry_run:
        logger.info(
            f"[dry-run] Email to={msg.to} from={from_name} <{from_email}>\nSubject: {msg.subject}\n\n{msg.body}"
        )
        return

    # Try SendGrid first
    if (
        SENDGRID_AVAILABLE
        and settings.SENDGRID_API_KEY
        and settings.SENDGRID_FROM_EMAIL
    ):
        _sendgrid_send(from_email, from_name, msg.to, msg.subject, msg.body)
        return

    # Fallback to SMTP
    if settings.SMTP_HOST and settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
        _smtp_send(from_email, from_name, msg.to, msg.subject, msg.body)
        return

    logger.warning(
        "No email provider configured. Set SENDER_DRY_RUN=true or provide SENDGRID_API_KEY or SMTP_ env vars."
    )


def _sendgrid_send(
    from_email: str, from_name: str, to_email: str, subject: str, body: str
) -> None:
    client = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    message = Mail(
        from_email=settings.SENDGRID_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=body.replace("\n", "<br>"),
    )
    response = client.send(message)
    logger.info(f"SendGrid response: {response.status_code}")


def _smtp_send(
    from_email: str, from_name: str, to_email: str, subject: str, body: str
) -> None:
    message = SmtpEmailMessage()
    message["From"] = f"{from_name} <{from_email}>"
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    host = settings.SMTP_HOST
    port = settings.SMTP_PORT
    username = settings.SMTP_USERNAME
    password = settings.SMTP_PASSWORD
    use_tls = settings.SMTP_USE_TLS
    logger.info(f"Sending via SMTP host={host}:{port} tls={use_tls}")
    if use_tls:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(message)
    else:
        with smtplib.SMTP(host, port) as server:
            server.login(username, password)
            server.send_message(message)
    logger.info("Email sent")
