import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL")
    
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

    SMTP_LOGIN = os.getenv("SMTP_LOGIN")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

    FROM_EMAIL = os.getenv("FROM_EMAIL")
    BREVO_API_KEY = os.getenv("BREVO_API_KEY")
