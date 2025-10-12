import os
from dotenv import load_dotenv

load_dotenv()  # local dev

SMTP_CONFIG = {
    "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
    "port": int(os.getenv("SMTP_PORT", 587)),  # 587 is STARTTLS
    "user": os.getenv("SMTP_USER"),            # your Gmail email
    "password": os.getenv("SMTP_PASS"),        # Gmail app password
    "to_email": os.getenv("TO_EMAIL")          # destination email
}
