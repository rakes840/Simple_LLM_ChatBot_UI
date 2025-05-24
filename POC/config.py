import os
from dotenv import load_dotenv

load_dotenv()

APP_TITLE = "AI Chatbot"
PAGE_ICON = "🤖"
LAYOUT = "wide"
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_FILE = "logs/app.log"

HF_MODEL_NAME = os.getenv("HF_MODEL_NAME", "google/flan-t5-xxl")  # Default model
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.5"))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")  # SQLite default

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-default-secret-key")  # Change this!
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_TIME = 3600  # Seconds (1 hour)

RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY", "")  # Get from Google reCAPTCHA
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "")
