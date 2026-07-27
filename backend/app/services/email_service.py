import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings


def send_report_email(to_email: str, report_text: str, subject: str = "Your SEO Audit Report") -> bool:
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        print("[email_service] SMTP not configured — skipping email send.")
        return False

    msg = MIMEMultipart()
    msg["From"] = settings.EMAIL_FROM or settings.SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(report_text, "plain"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT or 587) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as exc:
        print(f"[email_service] Failed to send email: {exc}")
        return False
