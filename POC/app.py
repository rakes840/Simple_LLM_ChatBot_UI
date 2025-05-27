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
    update_feedback,
    format_timestamp,
)
from config import APP_TITLE, PAGE_ICON, LAYOUT

logger = logging.getLogger(__name__)

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

def show_profile_section():
    if st.session_state.get("show_profile", False):
        with st.container():
            st.markdown("### Profile Details")
            username = st.text_input("Username", value=st.session_state.username, key="profile_username")
            email = st.text_input("Email", value=st.session_state.email, key="profile_email")
            if st.button("Update Profile"):
                updated = update_user_profile(st.session_state.user_id, username, email)
                if updated:
                    st.success("Profile updated successfully.")
                    st.session_state.username = username
                    st.session_state.email = email
                else:
                    st.error("Failed to update profile.")
            if st.button("Close Profile"):
                st.session_state.show_profile = False
                st.experimental_rerun()
    else:
        if st.button("Profile"):
            st.session_state.show_profile = True
            st.experimental_rerun()

def main_chat_interface():
    st.header("Chat Interface")

    user_id = st.session_state.user_id
    sessions = get_user_chat_sessions(user_id)
    if sessions:
        session_names = [s.session_name or f"Session {s.id}" for s in sessions]
        session_ids = [s.id for s in sessions]
        selected_session_idx = st.radio("Select Chat Session", range(len(session_names)), format_func=lambda i: session_names[i])
        selected_session_id = session_ids[selected_session_idx]
        st.session_state.selected_session_id = selected_session_id
    else:
        st.info("No chat sessions found. Start a new chat.")

    if "selected_session_id" in st.session_state:
        chat_history = get_session_chat_history(user_id, st.session_state.selected_session_id)
    else:
        chat_history = []

    chat_container = st.container()
    with chat_container:
        for chat in chat_history:
            st.markdown(f"**You:** {chat.user_message}")
            st.markdown(f"**Bot:** {chat.bot_response}")

    input_col, file_col, send_col = st.columns([7, 2, 1])
    with input_col:
        user_input = st.text_input("Your message", key="user_input", placeholder="Type your message here...")
    with file_col:
        uploaded_file = st.file_uploader("Attach file", key="file_uploader")
    with send_col:
        send_clicked = st.button("Send")

    if send_clicked and user_input:
        chatbot = get_chatbot()
        user_input_clean = sanitize_input(user_input)
        if uploaded_file:
            file_text = process_uploaded_file(uploaded_file)
            user_input_clean += f"\n\n[Attached file content]:\n{file_text}"

        response = chatbot.get_response(user_input_clean, user_id, st.session_state.get("selected_session_id"))
        chatbot.save_conversation(user_id, user_input_clean, response, st.session_state.get("selected_session_id"))

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        st.session_state.chat_history.append({"user": user_input_clean, "bot": response})
        st.experimental_rerun()

def main():
    if not st.session_state.get("authenticated", False):
        login_form()
    else:
        st.sidebar.title(f"Hello, {st.session_state.username}")
        show_profile_section()
        main_chat_interface()

if __name__ == "__main__":
    main()
