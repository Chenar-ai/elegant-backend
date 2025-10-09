import smtplib
from email.message import EmailMessage
from app.config import SMTP_CONFIG

def send_contact_email(from_email: str, subject: str, message: str):
    msg = EmailMessage()
    msg['Subject'] = subject or 'New Contact Form Message'
    msg['From'] = SMTP_CONFIG["user"]
    msg['To'] = SMTP_CONFIG["to_email"]
    msg.set_content(f"From: {from_email}\n\n{message}")

    try:
        with smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"]) as server:
            server.starttls()
            server.login(SMTP_CONFIG["user"], SMTP_CONFIG["password"])
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False
