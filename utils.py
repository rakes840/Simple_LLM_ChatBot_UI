import streamlit as st
import datetime
from db import ChatHistory, get_db

def get_user_chat_history(user_id):
   """Get chat history for a specific user."""
   db = get_db()
   history = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).order_by(ChatHistory.timestamp).all()
   return history

def format_chat_history(history):
   """Format chat history for display in the sidebar."""
   formatted_history = []
   for chat in history:
       date_str = chat.timestamp.strftime("%Y-%m-%d %H:%M")
       # Truncate long messages for display
       user_msg = chat.user_message[:30] + "..." if len(chat.user_message) > 30 else chat.user_message
       formatted_history.append(f"{date_str}: {user_msg}")
   return formatted_history

def format_timestamp(timestamp):
   """Format timestamp for display."""
   return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def initialize_session_state():
   """Initialize session state variables."""
   if 'user_id' not in st.session_state:
       st.session_state.user_id = None
   if 'username' not in st.session_state:
       st.session_state.username = None
   if 'authenticated' not in st.session_state:
       st.session_state.authenticated = False
   if 'chat_history' not in st.session_state:
       st.session_state.chat_history = []
   if 'messages' not in st.session_state:
       st.session_state.messages = []
       
def load_css():
   """Load custom CSS for the app."""
   with open("styles/main.css", "r") as f:
       css = f.read()
   return css