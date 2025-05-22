# Application Configuration Settings
# Hugging Face Model Configuration
HF_MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"  # Default HF model, you can change as needed
MAX_NEW_TOKENS = 512
TEMPERATURE = 0.7

# Streamlit UI Configuration
APP_TITLE = "LangChain Hugging Face Chatbot"
PAGE_ICON = "🤖"
LAYOUT = "wide"

# Authentication Configuration
SESSION_EXPIRY_DAYS = 30

# Database Configuration
DB_PATH = "db/chatbot.db"

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "logs/app.log"
