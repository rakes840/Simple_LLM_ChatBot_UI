import streamlit as st
import os
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from db import create_tables, get_db, ChatHistory, ChatSession
from auth import create_user, authenticate_user, validate_password_strength, update_user_profile
from chatbot import get_chatbot
from utils import (
    get_user_chat_sessions,
    get_session_chat_history,
    format_chat_sessions,
    sanitize_input,
    process_uploaded_file,
    initialize_session_state,
    update_feedback
)
from config import APP_TITLE, PAGE_ICON, LAYOUT
from streamlit_extras.copy_to_clipboard import copy_to_clipboard

# Setup logging
logger = logging.getLogger(__name__)

# Initialize app
os.makedirs("db", exist_ok=True)
os.makedirs("styles", exist_ok=True)
os.makedirs("logs", exist_ok=True)
create_tables()

st.set_page_config(page_title=APP_TITLE, page_icon=PAGE_ICON, layout=LAYOUT)
initialize_session_state()

executor = ThreadPoolExecutor(max_workers=10)

def load_css():
    css_path = "styles/main.css"
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        logger.warning("CSS file not found.")

load_css()

def login_form():
    st.title("Welcome to LangChain Hugging Face Chatbot")
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_button"):
            if not username or not password:
                st.warning("Please enter both username and password.")
                return
            try:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.user_id = user["id"]
                    st.session_state.username = user["username"]
                    st.session_state.email = user.get("email", "")
                    st.session_state.authenticated = True
                    st.success(f"Welcome back, {user['username']}!")
                    time.sleep(1)
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password.")
            except Exception as e:
                logger.error(f"Login error: {str(e)}")
                st.error("An error occurred during login. Please try again later.")

    with tab2:
        st.subheader("Register")
        new_username = st.text_input("Username", key="register_username")
        new_email = st.text_input("Email", key="register_email")
        new_password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

        if st.button("Register", key="register_button"):
            if not new_username or not new_email or not new_password:
                st.warning("Please fill in all fields.")
                return
            if new_password != confirm_password:
                st.error("Passwords do not match.")
                return
            password_validation = validate_password_strength(new_password)
            if not password_validation["valid"]:
                st.error(password_validation["message"])
                return
            try:
                user = create_user(new_username, new_email, new_password)
                if user:
                    st.success("Registration successful! Please log in.")
                else:
                    st.error("Username or email already exists or invalid.")
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                st.error("An error occurred during registration. Please try again later.")

def show_profile_editor():
    with st.form("profile_form"):
        new_username = st.text_input("Username", st.session_state.username)
        new_email = st.text_input("Email", st.session_state.email)
        submitted = st.form_submit_button("Update Profile")
        if submitted:
            success = update_user_profile(st.session_state.user_id, new_username, new_email)
            if success:
                st.success("Profile updated successfully!")
                st.session_state.username = new_username
                st.session_state.email = new_email
            else:
                st.error("Failed to update profile. Please try again.")

def format_message_with_timestamp(message):
    timestamp = message.get('timestamp', datetime.utcnow())
    if isinstance(timestamp, str):
        timestamp_str = timestamp
    else:
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M")
    background = "#e3f2fd" if message['role'] == 'user' else "#f5f5f5"
    return f"""
    <div style='margin: 0.5rem 0; padding: 0.5rem; border-radius: 0.5rem; background: {background}'>
        <div>{message['content']}</div>
        <div style='font-size: 0.8rem; color: #666; margin-top: 0.3rem'>{timestamp_str}</div>
    </div>
    """

def chat_interface():
    chatbot = get_chatbot()

    with st.sidebar:
        st.subheader("Profile")
        st.write(f"**Username:** {st.session_state.username}")
        st.write(f"**Email:** {st.session_state.email}")
        if st.button("Edit Profile"):
            show_profile_editor()

        if st.button("Reset Conversation"):
            chatbot.reset_memory(str(st.session_state.user_id), str(st.session_state.current_session_id))
            st.session_state.messages = []
            st.success("Conversation reset!")

        if st.button("New Chat"):
            st.session_state.messages = []
            st.session_state.current_session_id = None
            st.session_state.current_session_name = None
            st.experimental_rerun()

        if st.button("Logout"):
            st.session_state.clear()
            st.experimental_rerun()

        st.markdown("---")
        st.header("Past Conversations")
        try:
            sessions = get_user_chat_sessions(st.session_state.user_id)
            if sessions:
                formatted_sessions = format_chat_sessions(sessions)
                selected_session_idx = st.radio(
                    "Select a previous conversation:",
                    range(len(formatted_sessions)),
                    format_func=lambda i: formatted_sessions[i],
                    key="chat_sessions_radio",
                )
                if st.button("Load Selected Chat"):
                    session = sessions[selected_session_idx]
                    if st.session_state.current_session_id != session.id:
                        st.session_state.current_session_id = session.id
                        st.session_state.current_session_name = session.session_name
                        with st.spinner("Loading conversation..."):
                            st.session_state.messages = []
                            chatbot.reset_memory(str(st.session_state.user_id), str(session.id))
                            chatbot.load_conversation_history(st.session_state.user_id, session.id)
                            session_messages = get_session_chat_history(session.id)
                            for message in session_messages:
                                st.session_state.messages.append({
                                    "role": "user",
                                    "content": message.user_message,
                                    "timestamp": message.timestamp
                                })
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": message.bot_response,
                                    "timestamp": message.timestamp
                                })
                        st.experimental_rerun()
            else:
                st.info("No past conversations available.")
        except Exception as e:
            logger.error(f"Error loading chat sessions: {str(e)}")
            st.error("Failed to load chat sessions.")

    st.title("🤖 LangChain Hugging Face Chatbot")
    st.markdown("---")

    # Display chat messages with timestamps and copy button
    for message in st.session_state.get("messages", []):
        with st.chat_message(message["role"]):
            st.markdown(format_message_with_timestamp(message), unsafe_allow_html=True)
            if message["role"] == "assistant":
                copy_to_clipboard(message["content"], "📋 Copy Response", key=f"copy_{message.get('timestamp', '')}")

    # File uploader
    uploaded_file = st.file_uploader("Upload file", type=["txt", "pdf", "docx"], label_visibility="visible")
    user_input = st.chat_input("Type your message here...")

    if uploaded_file:
        file_content = process_uploaded_file(uploaded_file)
        user_input = f"[File: {uploaded_file.name}] {file_content}"

    if user_input:
        user_input = sanitize_input(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": datetime.utcnow()})
        with st.chat_message("user"):
            st.write(user_input)

        with st.spinner("Thinking..."):
            try:
                if st.session_state.current_session_id is None:
                    with get_db() as db:
                        new_session = ChatSession(
                            user_id=st.session_state.user_id,
                            session_name=user_input,
                        )
                        db.add(new_session)
                        db.commit()
                        db.refresh(new_session)
                        st.session_state.current_session_id = new_session.id
                        st.session_state.current_session_name = user_input

                bot_response = chatbot.get_response(
                    user_input,
                    str(st.session_state.user_id),
                    str(st.session_state.current_session_id)
                )
                bot_response = sanitize_input(bot_response)
                st.session_state.messages.append({"role": "assistant", "content": bot_response, "timestamp": datetime.utcnow()})

                with st.chat_message("assistant"):
                    st.write(bot_response)
                    copy_to_clipboard(bot_response, "📋 Copy Response", key=f"copy_{datetime.utcnow()}")

                # Save chat history
                with get_db() as db:
                    chat_entry = ChatHistory(
                        session_id=st.session_state.current_session_id,
                        user_id=st.session_state.user_id,
                        user_message=user_input,
                        bot_response=bot_response,
                        timestamp=datetime.utcnow()
                    )
                    db.add(chat_entry)
                    db.commit()
            except Exception as e:
                logger.error(f"Error in chat processing: {str(e)}")
                st.error("An error occurred while processing your message.")

def main():
    if not st.session_state.authenticated:
        login_form()
    else:
        chat_interface()

if __name__ == "__main__":
    main()
