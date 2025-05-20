import asyncio
import os
import time
from datetime import datetime
from functools import lru_cache
from typing import List, Dict, Any, Optional
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError
from db import ChatHistory, get_db
from logger import get_logger

# Get logger
logger = get_logger()

@lru_cache(maxsize=100)
def get_user_chat_history(user_id: int, max_records: int = 100) -> List[ChatHistory]:
    """Get chat history for a specific user with caching for performance."""
    try:
        start_time = time.time()
        with get_db() as db:
            history = db.query(ChatHistory).filter(
                ChatHistory.user_id == user_id
            ).order_by(ChatHistory.timestamp.desc()).limit(max_records).all()
            
            logger.info(f"Retrieved {len(history)} history records in {time.time() - start_time:.3f}s")
            return list(reversed(history))  # Return in chronological order
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_user_chat_history: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in get_user_chat_history: {str(e)}")
        return []

def format_chat_history(history: List[ChatHistory]) -> List[str]:
    """Format chat history for display in the sidebar."""
    try:
        formatted_history = []
        for chat in history:
            date_str = chat.timestamp.strftime("%m-%d %H:%M")
            # Truncate long messages for display
            user_msg = chat.user_message[:30] + "..." if len(chat.user_message) > 30 else chat.user_message
            formatted_history.append(f"{date_str}: {user_msg}")
        return formatted_history
    except Exception as e:
        logger.error(f"Error formatting chat history: {str(e)}")
        return ["Error loading history"]

def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for display."""
    try:
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "Invalid timestamp"

def initialize_session_state() -> None:
    """Initialize session state variables."""
    try:
        # Define all required session state variables
        required_vars = {
            'user_id': None,
            'username': None,
            'authenticated': False,
            'chat_history': [],
            'messages': [],
            'loaded_history': False,
            'error': None,
            'login_attempts': 0,
            'last_attempt_time': None
        }
        
        # Initialize any missing variables
        for var, default in required_vars.items():
            if var not in st.session_state:
                st.session_state[var] = default
    except Exception as e:
        logger.error(f"Error initializing session state: {str(e)}")

def load_css() -> str:
    """Load custom CSS for the app with caching."""
    try:
        css_path = "styles/main.css"
        if os.path.exists(css_path):
            with open(css_path, "r") as f:
                return f.read()
        else:
            logger.warning("CSS file not found")
            return ""
    except Exception as e:
        logger.error(f"Error loading CSS: {str(e)}")
        return ""

def clear_session_on_logout() -> None:
    """Clear all session state variables on logout."""
    try:
        keys_to_preserve = ['login_attempts', 'last_attempt_time']
        preserved_values = {key: st.session_state.get(key) for key in keys_to_preserve}
        
        # Clear session state
        for key in list(st.session_state.keys()):
            if key not in keys_to_preserve:
                del st.session_state[key]
        
        # Reinitialize with preserved values
        initialize_session_state()
        
        # Restore preserved values
        for key, value in preserved_values.items():
            st.session_state[key] = value
            
        logger.info("Session cleared on logout")
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")

def handle_error(error_message: str, log_error: bool = True) -> None:
    """Handle and display errors."""
    if log_error:
        logger.error(error_message)
    st.error(error_message)
    time.sleep(2)  # Give user time to read the error

async def fetch_chat_history_async(user_id: int, max_records: int = 100) -> List[ChatHistory]:
    """Asynchronously fetch chat history."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, 
        lambda: get_user_chat_history(user_id, max_records)
    )

# Added setup_logging function to match app.py references
def setup_logging(level="INFO", log_format=None, log_file=None):
    """Set up application logging - wrapper for logger.setup_logging"""
    from logger import setup_logging as logger_setup
    return logger_setup(level, log_format, log_file)
