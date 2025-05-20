import streamlit as st
import os
import time
import logging
import traceback
import asyncio
from concurrent.futures import ThreadPoolExecutor
from streamlit.components.v1 import html
from db import create_tables, get_db, ChatHistory
from auth import create_user, authenticate_user, validate_password_strength
from chatbot import get_chatbot
from utils import get_user_chat_history, format_chat_history, format_timestamp, initialize_session_state, setup_logging
from config import APP_TITLE, PAGE_ICON, LAYOUT, LOG_LEVEL, LOG_FORMAT, LOG_FILE

# Set up logging
setup_logging(LOG_LEVEL, LOG_FORMAT, LOG_FILE)
logger = logging.getLogger(__name__)

# Create necessary directories
try:
    os.makedirs('db', exist_ok=True)
    os.makedirs('styles', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    # Create database tables
    create_tables()
    logger.info("Application initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize application: {str(e)}")
    st.error("Failed to initialize application. Please check the logs or contact an administrator.")

# Thread pool for background tasks
executor = ThreadPoolExecutor(max_workers=10)

# Page configuration
st.set_page_config(
   page_title=APP_TITLE,
   page_icon=PAGE_ICON,
   layout=LAYOUT
)

# Initialize session state
initialize_session_state()

# Custom CSS
def load_css():
    try:
        if os.path.exists("styles/main.css"):
            with open("styles/main.css", "r") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        else:
            logger.warning("CSS file not found. UI styling might be affected.")
            st.warning("CSS file not found. UI styling might be affected.")
    except Exception as e:
        logger.error(f"Failed to load CSS: {str(e)}")
        st.warning("Failed to load styling. The application will continue with default styling.")

load_css()

# Login Form
def login_form():
    st.title("Welcome to LangChain Hugging Face Chatbot")
    
    # Create tabs for login and registration
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
                    logger.info(f"User '{username}' logged in successfully")
                    st.session_state.user_id = user.id
                    st.session_state.username = user.username
                    st.session_state.authenticated = True
                    st.session_state.login_attempts = 0  # Reset login attempts
                    st.success(f"Welcome back, {username}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    # Track failed login attempts
                    if 'login_attempts' not in st.session_state:
                        st.session_state.login_attempts = 1
                    else:
                        st.session_state.login_attempts += 1
                    
                    logger.warning(f"Failed login attempt for username '{username}' (Attempt #{st.session_state.login_attempts})")
                    
                    if st.session_state.login_attempts >= 5:
                        st.error("Too many failed login attempts. Please try again later.")
                        time.sleep(3)  # Add a delay to discourage brute force attacks
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
                
                # Validate password strength
                password_validation = validate_password_strength(new_password)
                if not password_validation['valid']:
                    st.error(password_validation['message'])
                    return
                
                with st.spinner("Creating account..."):
                    user = create_user(new_username, new_email, new_password)
                
                if user:
                    logger.info(f"New user registered: {new_username}")
                    st.success("Registration successful! Please log in.")
                else:
                    st.error("Username or email already exists. Please choose another one.")
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                st.error("An error occurred during registration. Please try again later.")

# Function to get chatbot response asynchronously
def get_response_async(chatbot, user_input, user_id):
    try:
        return chatbot.get_response(user_input, user_id)
    except Exception as e:
        logger.error(f"Error getting chatbot response: {str(e)}\n{traceback.format_exc()}")
        return f"I'm sorry, I encountered an error while processing your request. Please try again later. Error: {str(e)}"

# Chat Interface
def chat_interface():
    try:
        # Create a layout with sidebar for chat history
        st.sidebar.title(f"Welcome, {st.session_state.username}!")
        
        # Logout button in sidebar
        if st.sidebar.button("Logout", key="logout_button"):
            logger.info(f"User '{st.session_state.username}' logged out")
            # Clear session state
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.authenticated = False
            st.session_state.chat_history = []
            st.session_state.messages = []
            st.session_state.loaded_history = False
            st.rerun()
        
        st.sidebar.markdown("---")
        st.sidebar.header("Chat History")
        
        # Get user chat history from database
        with st.spinner("Loading chat history..."):
            try:
                history = get_user_chat_history(st.session_state.user_id)
            except Exception as e:
                logger.error(f"Error loading chat history: {str(e)}")
                st.sidebar.error("Failed to load chat history. Please refresh the page.")
                history = []
        
        # Format history for sidebar display
        if history:
            try:
                formatted_history = format_chat_history(history)
                selected_chat_idx = st.sidebar.radio(
                    "Select a previous conversation:",
                    range(len(formatted_history)),
                    format_func=lambda i: formatted_history[i],
                    key="chat_history_radio"
                )
            except Exception as e:
                logger.error(f"Error formatting chat history: {str(e)}")
                st.sidebar.error("Failed to display chat history properly.")
        else:
            st.sidebar.info("No chat history available.")
        
        # Main chat area
        st.title("🤖 LangChain Hugging Face Chatbot")
        st.markdown("---")
        
        # Initialize chatbot
        try:
            chatbot = get_chatbot()
        except Exception as e:
            logger.critical(f"Failed to initialize chatbot: {str(e)}")
            st.error("Failed to initialize chatbot. Please try refreshing the page or contact an administrator.")
            return
        
        # Load chat history into memory if needed
        if 'loaded_history' not in st.session_state or not st.session_state.loaded_history:
            try:
                with st.spinner("Loading conversation history..."):
                    chatbot.load_conversation_history(st.session_state.user_id)
                st.session_state.loaded_history = True
            except Exception as e:
                logger.error(f"Error loading conversation history: {str(e)}")
                st.warning("Failed to load previous conversations. Starting with a fresh conversation.")
                st.session_state.loaded_history = True  # Avoid repeated loading attempts
        
        # Display messages
        if history and ('messages' not in st.session_state or not st.session_state.messages):
            try:
                st.session_state.messages = []
                for chat in history:
                    st.session_state.messages.append({"role": "user", "content": chat.user_message})
                    st.session_state.messages.append({"role": "assistant", "content": chat.bot_response})
            except Exception as e:
                logger.error(f"Error loading messages from history: {str(e)}")
                st.warning("Failed to load message history properly.")
        
        # Display chat messages
        try:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        except Exception as e:
            logger.error(f"Error displaying chat messages: {str(e)}")
            st.error("Failed to display chat messages properly. Please refresh the page.")
        
        # Chat input
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)
            
            # Get bot response using thread pool
            with st.spinner("Thinking..."):
                try:
                    # Submit task to thread pool
                    future = executor.submit(get_response_async, chatbot, user_input, st.session_state.user_id)
                    
                    # Add timeout to prevent blocking indefinitely
                    bot_response = future.result(timeout=60)  # 60-second timeout
                    
                    # Add bot response to chat
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                    with st.chat_message("assistant"):
                        st.write(bot_response)
                except TimeoutError:
                    logger.error(f"Timeout getting response for user '{st.session_state.username}'")
                    st.error("The chatbot took too long to respond. Please try again with a shorter or clearer message.")
                except Exception as e:
                    logger.error(f"Error in chat processing: {str(e)}")
                    st.error("An error occurred while processing your message. Please try again.")
    except Exception as e:
        logger.error(f"Chat interface error: {str(e)}\n{traceback.format_exc()}")
        st.error("An unexpected error occurred. Please refresh the page or contact an administrator.")

# Main app logic
def main():
    try:
        if not st.session_state.authenticated:
            login_form()
        else:
            chat_interface()
    except Exception as e:
        logger.critical(f"Critical application error: {str(e)}\n{traceback.format_exc()}")
        st.error("An unexpected error occurred. Please refresh the page or contact an administrator.")

if __name__ == "__main__":
    main()
