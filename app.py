import streamlit as st
import os
import time
from streamlit.components.v1 import html
from db import create_tables, get_db, ChatHistory
from auth import create_user, authenticate_user
from chatbot import get_chatbot
from utils import get_user_chat_history, format_chat_history, format_timestamp, initialize_session_state
from config import APP_TITLE, PAGE_ICON, LAYOUT
# Create database directory and tables
os.makedirs('db', exist_ok=True)
os.makedirs('styles', exist_ok=True)
create_tables()
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
   if os.path.exists("styles/main.css"):
       with open("styles/main.css", "r") as f:
           st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
   else:
       st.warning("CSS file not found. UI styling might be affected.")
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
           if username and password:
               user = authenticate_user(username, password)
               if user:
                   st.session_state.user_id = user.id
                   st.session_state.username = user.username
                   st.session_state.authenticated = True
                   st.success(f"Welcome back, {username}!")
                   time.sleep(1)
                   st.rerun()
               else:
                   st.error("Invalid username or password.")
           else:
               st.warning("Please enter both username and password.")
   with tab2:
       st.subheader("Register")
       new_username = st.text_input("Username", key="register_username")
       new_email = st.text_input("Email", key="register_email")
       new_password = st.text_input("Password", type="password", key="register_password")
       confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
       if st.button("Register", key="register_button"):
           if new_username and new_email and new_password:
               if new_password != confirm_password:
                   st.error("Passwords do not match.")
               else:
                   user = create_user(new_username, new_email, new_password)
                   if user:
                       st.success("Registration successful! Please log in.")
                   else:
                       st.error("Username already exists. Please choose another one.")
           else:
               st.warning("Please fill in all fields.")
# Chat Interface
def chat_interface():
# Create a layout with sidebar for chat history
   st.sidebar.title(f"Welcome, {st.session_state.username}!")
# Logout button in sidebar
   if st.sidebar.button("Logout", key="logout_button"):
# Clear session state
       st.session_state.user_id = None
       st.session_state.username = None
       st.session_state.authenticated = False
       st.session_state.chat_history = []
       st.session_state.messages = []
       st.rerun()
   st.sidebar.markdown("---")
   st.sidebar.header("Chat History")
# Get user chat history from database
   history = get_user_chat_history(st.session_state.user_id)
# Format history for sidebar display
   if history:
       formatted_history = format_chat_history(history)
       selected_chat_idx = st.sidebar.radio(
           "Select a previous conversation:",
           range(len(formatted_history)),
           format_func=lambda i: formatted_history[i],
           key="chat_history_radio"
       )
   else:
       st.sidebar.info("No chat history available.")
# Main chat area
   st.title("🤖 LangChain Hugging Face Chatbot")
   st.markdown("---")
# Initialize chatbot
   chatbot = get_chatbot()
# Load chat history into memory if needed
   if 'loaded_history' not in st.session_state or not st.session_state.loaded_history:
       chatbot.load_conversation_history(st.session_state.user_id)
       st.session_state.loaded_history = True
# Display messages
   if history:
       if 'messages' not in st.session_state or not st.session_state.messages:
           st.session_state.messages = []
           for chat in history:
               st.session_state.messages.append({"role": "user", "content": chat.user_message})
               st.session_state.messages.append({"role": "assistant", "content": chat.bot_response})
# Display chat messages
   for message in st.session_state.messages:
       with st.chat_message(message["role"]):
           st.write(message["content"])
# Chat input
   user_input = st.chat_input("Type your message here...")
   if user_input:
# Add user message to chat
       st.session_state.messages.append({"role": "user", "content": user_input})
       with st.chat_message("user"):
           st.write(user_input)
# Get bot response
       with st.spinner("Thinking..."):
           bot_response = chatbot.get_response(user_input, st.session_state.user_id)
# Add bot response to chat
       st.session_state.messages.append({"role": "assistant", "content": bot_response})
       with st.chat_message("assistant"):
           st.write(bot_response)
# Main app logic
def main():
   if not st.session_state.authenticated:
       login_form()
   else:
       chat_interface()
if __name__ == "__main__":
   main()