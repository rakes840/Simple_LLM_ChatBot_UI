import streamlit as st
import os
import time
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor

from db import create_tables, get_db, ChatHistory, ChatSession
from auth import create_user, authenticate_user, validate_password_strength
from chatbot import get_chatbot
from utils import (
    get_user_chat_history,
    format_chat_history,
    initialize_session_state,
    setup_logging,
    get_session_chat_history,
    format_chat_sessions,
    get_user_chat_sessions,
)
from config import APP_TITLE, PAGE_ICON, LAYOUT, LOG_LEVEL, LOG_FORMAT, LOG_FILE

# Set up logging
setup_logging(LOG_LEVEL, LOG_FORMAT, LOG_FILE)
logger = logging.getLogger(__name__)

# Create necessary directories
try:
    os.makedirs("db", exist_ok=True)
    os.makedirs("styles", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    create_tables()
    logger.info("Application initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize application: {str(e)}")
    st.error("Failed to initialize application. Please check the logs or contact an administrator.")

# Thread pool for background tasks
executor = ThreadPoolExecutor(max_workers=10)

# Page configuration
st.set_page_config(page_title=APP_TITLE, page_icon=PAGE_ICON, layout=LAYOUT)

# Initialize session state
initialize_session_state()

# Custom CSS
def load_css():
    try:
        css_path = "styles/main.css"
        if os.path.exists(css_path):
            with open(css_path, "r") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        else:
            logger.warning("CSS file not found. UI styling might be affected.")
    except Exception as e:
        logger.error(f"Failed to load CSS: {str(e)}")

load_css()

# Login Form
def login_form():
    st.title("Welcome to LangChain Hugging Face Chatbot")
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="login_button"):
            try:
                if not username or not password:
                    st.warning("Please enter both username and password.")
                    return
                with st.spinner("Authenticating..."):
                    user = authenticate_user(username, password)
                if user:
                    logger.info(f"User '{user['username']}' logged in successfully")
                    st.session_state.user_id = user["id"]
                    st.session_state.username = user["username"]
                    st.session_state.authenticated = True
                    st.session_state.login_attempts = 0
                    st.success(f"Welcome back, {user['username']}!")
                    time.sleep(1)
                    st.experimental_rerun()
                else:
                    st.session_state.login_attempts = st.session_state.get("login_attempts", 0) + 1
                    logger.warning(
                        f"Failed login attempt for username '{username}' (Attempt #{st.session_state.login_attempts})"
                    )
                    if st.session_state.login_attempts >= 5:
                        st.error("Too many failed login attempts. Please try again later.")
                        time.sleep(3)
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
            try:
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
                with st.spinner("Creating account..."):
                    user = create_user(new_username, new_email, new_password)
                if user:
                    logger.info(f"New user registered: {new_username}")
                    st.success("Registration successful! Please log in.")
                else:
                    st.error("Username or email already exists or invalid. Please choose another one.")
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                st.error("An error occurred during registration. Please try again later.")

# Function to get chatbot response synchronously (for thread pool)
def get_response_sync(chatbot, user_input, user_id, current_session_id):
    try:
        response = chatbot.get_response(user_input, user_id)
        return response
    except Exception as e:
        logger.error(f"Error getting chatbot response: {str(e)}\n{traceback.format_exc()}")
        return f"I'm sorry, I encountered an error while processing your request. Please try again later. Error: {str(e)}"

# Chat Interface
def chat_interface():
    try:
        st.sidebar.title(f"Welcome, {st.session_state.username}!")
        # Logout button
        if st.sidebar.button("Logout", key="logout_button"):
            logger.info(f"User '{st.session_state.username}' logged out")
            st.session_state.clear()
            st.experimental_rerun()
        # New Chat button
        if st.sidebar.button("New Chat", key="new_chat_button"):
            # Save current session messages if any
            if (
                st.session_state.get("current_session_id")
                and st.session_state.get("messages")
                and len(st.session_state.messages) > 0
            ):
                try:
                    with get_db() as db:
                        msgs = st.session_state.messages
                        for i in range(0, len(msgs), 2):
                            user_msg = msgs[i]["content"]
                            bot_msg = msgs[i + 1]["content"] if i + 1 < len(msgs) else ""
                            chat_entry = ChatHistory(
                                session_id=st.session_state.current_session_id,
                                user_message=user_msg,
                                bot_response=bot_msg,
                            )
                            db.add(chat_entry)
                        db.commit()
                        logger.info(
                            f"Saved chat history for session {st.session_state.current_session_id} before starting new chat"
                        )
                except Exception as e:
                    logger.error(f"Error saving chat history on New Chat: {str(e)}")
            st.session_state.messages = []
            st.session_state.current_session_id = None
            st.session_state.current_session_name = None
            # --- Reset the radio button selection ---
            if "chat_sessions_radio" in st.session_state:
                del st.session_state["chat_sessions_radio"]
            st.experimental_rerun()

        st.sidebar.markdown("---")
        st.sidebar.header("Past Conversations")
        try:
            sessions = get_user_chat_sessions(st.session_state.user_id)
            if sessions:
                formatted_sessions = format_chat_sessions(sessions)
                selected_session_idx = st.sidebar.radio(
                    "Select a previous conversation:",
                    range(len(formatted_sessions)),
                    format_func=lambda i: formatted_sessions[i],
                    key="chat_sessions_radio",
                )
                # --- LOAD CHAT HISTORY AS SOON AS RADIO BUTTON CHANGES ---
                session = sessions[selected_session_idx]
                # Only load if current session is not the same as selected
                if (
                    st.session_state.get("current_session_id") != session.id
                    or not st.session_state.get("messages")
                    or len(st.session_state.messages) == 0
                ):
                    st.session_state.current_session_id = session.id
                    st.session_state.current_session_name = session.session_name
                    with st.spinner("Loading conversation..."):
                        session_messages = get_session_chat_history(session.id)
                    st.session_state.messages = []
                    for message in session_messages:
                        st.session_state.messages.append({"role": "user", "content": message.user_message})
                        st.session_state.messages.append({"role": "assistant", "content": message.bot_response})
                    st.experimental_rerun()
            else:
                st.sidebar.info("No past conversations available.")
        except Exception as e:
            logger.error(f"Error loading chat sessions: {str(e)}")
            st.sidebar.error("Failed to load chat sessions.")

        st.sidebar.markdown("---")

        st.title("🤖 LangChain Hugging Face Chatbot")
        st.markdown("---")
        try:
            chatbot = get_chatbot()
        except Exception as e:
            logger.critical(f"Failed to initialize chatbot: {str(e)}")
            st.error("Failed to initialize chatbot. Please try refreshing the page or contact an administrator.")
            return

        if "messages" not in st.session_state:
            st.session_state.messages = []

        try:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        except Exception as e:
            logger.error(f"Error displaying chat messages: {str(e)}")
            st.error("Failed to display chat messages properly. Please refresh the page.")

        user_input = st.chat_input("Type your message here...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)
            with st.spinner("Thinking..."):
                try:
                    if st.session_state.current_session_id is None:
                        try:
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
                                logger.info(
                                    f"Created new chat session {new_session.id} for user {st.session_state.user_id}"
                                )
                        except Exception as e:
                            logger.error(f"Error creating chat session: {str(e)}")
                    future = executor.submit(
                        get_response_sync,
                        chatbot,
                        user_input,
                        st.session_state.user_id,
                        st.session_state.current_session_id,
                    )
                    bot_response = future.result(timeout=60)
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                    with st.chat_message("assistant"):
                        st.write(bot_response)
                    try:
                        with get_db() as db:
                            chat_entry = ChatHistory(
                                session_id=st.session_state.current_session_id,
                                user_message=user_input,
                                bot_response=bot_response,
                            )
                            db.add(chat_entry)
                            db.commit()
                    except Exception as e:
                        logger.error(f"Error saving chat history: {str(e)}")
                except TimeoutError:
                    logger.error(f"Timeout getting response for user '{st.session_state.username}'")
                    st.error("The chatbot took too long to respond. Please try again with a shorter or clearer message.")
                except Exception as e:
                    logger.error(f"Error in chat processing: {str(e)}")
                    st.error("An error occurred while processing your message. Please try again.")
    except Exception as e:
        logger.error(f"Chat interface error: {str(e)}\n{traceback.format_exc()}")
        st.error("An unexpected error occurred. Please refresh the page or contact an administrator.")

def main():
    if not st.session_state.authenticated:
        login_form()
    else:
        chat_interface()

if __name__ == "__main__":
    main()
