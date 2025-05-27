import streamlit as st
from db import get_db, ChatSession, ChatHistory
import datetime

def initialize_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "email" not in st.session_state:
        st.session_state.email = ""
    if "show_profile" not in st.session_state:
        st.session_state.show_profile = False
    if "selected_session_id" not in st.session_state:
        st.session_state.selected_session_id = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

def sanitize_input(user_input: str) -> str:
    return user_input.strip()

def process_uploaded_file(uploaded_file) -> str:
    if uploaded_file is not None:
        try:
            content = uploaded_file.read()
            try:
                return content.decode("utf-8")
            except UnicodeDecodeError:
                return "File content could not be decoded."
        except Exception as e:
            return f"Error reading file: {str(e)}"
    return ""

def get_user_chat_sessions(user_id: int):
    with get_db() as db:
        sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.created_at.desc()).all()
        return sessions

def get_session_chat_history(user_id: int, session_id: int):
    with get_db() as db:
        chats = (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id, ChatHistory.session_id == session_id)
            .order_by(ChatHistory.timestamp)
            .all()
        )
        return chats

def update_feedback(chat_id: int, feedback: str):
    with get_db() as db:
        chat = db.query(ChatHistory).filter(ChatHistory.id == chat_id).first()
        if chat:
            chat.feedback = feedback
            db.commit()

def format_timestamp(timestamp):
    if timestamp:
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return ""

def format_chat_sessions(sessions):
    return [s.session_name or f"Session {s.id}" for s in sessions]
