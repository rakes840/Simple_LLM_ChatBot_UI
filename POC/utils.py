import bleach
import jwt
from datetime import datetime, timedelta
from db import get_db, ChatSession, ChatHistory, User
from logger import get_logger
from config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXP_DELTA_SECONDS

logger = get_logger()

def initialize_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "email" not in st.session_state:
        st.session_state.email = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    if "current_session_name" not in st.session_state:
        st.session_state.current_session_name = None

def sanitize_input(user_input):
    return bleach.clean(user_input)

def get_user_chat_sessions(user_id):
    with get_db() as db:
        sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.created_at.desc()).all()
        return sessions

def get_session_chat_history(session_id):
    with get_db() as db:
        chats = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(ChatHistory.timestamp.asc()).all()
        return chats

def format_chat_sessions(sessions):
    return [f"{session.session_name} ({session.created_at.strftime('%Y-%m-%d %H:%M')})" for session in sessions]

def format_chat_history(messages, include_timestamps=True):
    lines = []
    for msg in messages:
        role = getattr(msg, "role", None) or getattr(msg, "user_message", None) or "unknown"
        content = getattr(msg, "content", None) or getattr(msg, "bot_response", None) or ""
        timestamp = getattr(msg, "timestamp", None)
        prefix = "Human" if role == "user" else "AI"
        ts_str = timestamp.strftime("%Y-%m-%d %H:%M") if timestamp and include_timestamps else ""
        lines.append(f"{prefix} [{ts_str}]: {content}" if ts_str else f"{prefix}: {content}")
    return "\n".join(lines)

def update_feedback(message_id, feedback):
    try:
        with get_db() as db:
            entry = db.query(ChatHistory).filter(ChatHistory.id == message_id).first()
            if entry:
                entry.feedback = feedback
                db.commit()
    except Exception as e:
        logger.error(f"Feedback update error: {str(e)}")

def process_uploaded_file(uploaded_file):
    try:
        content = ""
        if uploaded_file.type == "text/plain":
            content = uploaded_file.read().decode()
        elif uploaded_file.type == "application/pdf":
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
        else:
            content = "Unsupported file type."
        return content
    except Exception as e:
        logger.error(f"File processing error: {str(e)}")
        return "Error processing file."

def generate_jwt_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def setup_logging(level_str, log_format, log_file):
    from logger import setup_logging
    setup_logging(level_str, log_format, log_file)
