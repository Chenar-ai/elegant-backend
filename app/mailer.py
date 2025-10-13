import smtplib
from email.message import EmailMessage
from app.config import SMTP_CONFIG


def send_contact_email(from_email: str, subject: str, message: str):
    msg = EmailMessage()
    msg["Subject"] = subject or "New Contact Form Message"
    msg["From"] = SMTP_CONFIG["user"]
    msg["To"] = SMTP_CONFIG["to_email"]
    msg.set_content(f"From: {from_email}\n\n{message}")

    # Try SSL first (Namecheap supports this best)
    try:
        print("Trying SSL on port 465...")
        with smtplib.SMTP_SSL(SMTP_CONFIG["host"], 465, timeout=15) as server:
            server.set_debuglevel(1)
            server.login(SMTP_CONFIG["user"], SMTP_CONFIG["password"])
            server.send_message(msg)
        print("Email sent successfully via SSL!")
        return True
    except Exception as e:
        print(f"SSL failed: {e}")

    # Fallback to STARTTLS (port 587)
    try:
        print("Trying STARTTLS on port 587...")
        with smtplib.SMTP(SMTP_CONFIG["host"], 587, timeout=15) as server:
            server.set_debuglevel(1)
            server.starttls()
            server.login(SMTP_CONFIG["user"], SMTP_CONFIG["password"])
            server.send_message(msg)
        print("Email sent successfully via STARTTLS!")
        return True
    except Exception as e:
        print(f"STARTTLS failed: {e}")

    print("Email sending failed on both methods.")
    return False
