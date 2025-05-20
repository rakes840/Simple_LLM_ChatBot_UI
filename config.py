# Application Configuration Settings
# Hugging Face Model Configuration
HF_MODEL_NAME = "meta-llama/Llama-3.3-70B-Instructl"  # Default HF model, you can change as needed
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