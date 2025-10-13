import os
from dotenv import load_dotenv

load_dotenv()  # Load .env variables for local development

BREVO_CONFIG = {
    "api_key": os.getenv("BREVO_API_KEY"),
    "to_email": os.getenv("TO_EMAIL"),
}
