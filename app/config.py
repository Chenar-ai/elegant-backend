import os
from dotenv import load_dotenv

load_dotenv()

SMTP_CONFIG = {
    "host": os.getenv("SMTP_HOST"),
    "port": int(os.getenv("SMTP_PORT", 587)),  # fallback to 587 if not set
    "user": os.getenv("SMTP_USER"),
    "password": os.getenv("SMTP_PASS"),
    "to_email": os.getenv("TO_EMAIL")
}

# OpenAI API config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Supported languages for auto-translation
SUPPORTED_LANGUAGES = ["fr", "ar", "es", "de", "nl", "pt"]


