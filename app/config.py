import os
from dotenv import load_dotenv

load_dotenv()  # load .env for local development

SMTP_CONFIG = {
    "host": os.getenv("SMTP_HOST", "mail.privateemail.com"),
    "port": int(os.getenv("SMTP_PORT", 465)),
    "user": os.getenv("SMTP_USER"),
    "password": os.getenv("SMTP_PASS"),
    "to_email": os.getenv("TO_EMAIL"),
}
