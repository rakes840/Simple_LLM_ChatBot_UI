import streamlit as st
import bleach
import jwt
import time
import os
from datetime import datetime, timedelta
from db import get_db, ChatHistory, ChatSession, User
from config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_TIME

def initialize_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "email" not in st.session_state:
        st.session_state.email = ""
    if "last_login" not in st.session_state:
        st.session_state.last_login = None
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    if "current_session_name" not in st.session_state:
        st.session_state.current_session_name = None
    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0
    if "jwt_token" not in st.session_state:
        st.session_state.jwt_token = None  # For JWT
    if "show_profile_edit" not in st.session_state:
        st.session_state.show_profile_edit = False

def sanitize_input(user_input: str) -> str:
    # Clean user input to prevent XSS or injection attacks
    allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul', 'br', 'p']
    allowed_attributes = {'a': ['href', 'title'], 'abbr': ['title'], 'acronym': ['title']}
    return bleach.clean(user_input, tags=allowed_tags, attributes=allowed_attributes, strip=True)

def get_user_chat_sessions(user_id):
    try:
        with get_db() as db:
            sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.updated_at.desc()).all()
            return sessions
    except Exception:
        return []

def format_chat_sessions(sessions):
    return [f"{s.session_name} - {s.updated_at.strftime('%Y-%m-%d %H:%M:%S') if s.updated_at else ''}" for s in sessions]

def get_session_chat_history(session_id):
    try:
        with get_db() as db:
            messages = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(ChatHistory.timestamp.asc()).all()
            return messages
    except Exception:
        return []

def get_user_chat_history(user_id):
    try:
        with get_db() as db:
            sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).all()
            history = []
            for session in sessions:
                messages = db.query(ChatHistory).filter(ChatHistory.session_id == session.id).all()
                history.append((session, messages))
            return history
    except Exception:
        return []

def setup_logging(level, fmt, filename):
    import logging
    logging.basicConfig(
        level=level,
        format=fmt,
        handlers=[
            logging.FileHandler(filename),
            logging.StreamHandler()
        ]
    )

def create_jwt_token(user_id: int, username: str, email: str) -> str:
    """Creates a JWT token for a user."""
    payload = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "exp": datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION_TIME),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> dict:
    """Decodes a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Token is invalid

def verify_jwt_token(token: str) -> bool:
    """Verifies if the JWT token is valid."""
    return decode_jwt_token(token) is not None
