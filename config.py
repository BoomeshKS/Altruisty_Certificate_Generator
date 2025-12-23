import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_SCRIPT_URL = os.getenv('GOOGLE_SCRIPT_URL')
    EMAIL_USER = os.getenv('EMAIL_USER', 'hraltruisty@gmail.com')
    EMAIL_APP_PASSWORD = os.getenv('EMAIL_APP_PASSWORD')