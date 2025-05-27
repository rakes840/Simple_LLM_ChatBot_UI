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
        # Inline CSS as fallback
        st.markdown("""
        <style>
        .input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            border-top: 1px solid #e0e0e0;
            padding: 1rem;
            z-index: 1000;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        }
        .chat-messages {
            padding-bottom: 150px;
        }
        .message-actions {
            position: absolute;
            top: 10px;
            right: 10px;
            display: flex;
            gap: 5px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .chat-message:hover .message-actions {
            opacity: 1;
        }
        .action-btn {
            background: white;
            border: 1px solid #ddd;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 12px;
        }
        .profile-modal {
            position: fixed;
            top: 70px;
            left: 20px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            z-index: 1001;
            min-width: 250px;
            max-width: 300px;
        }
        .session-item {
            padding: 0.5rem;
            margin: 0.25rem 0;
            border-radius: 5px;
            cursor: pointer;
            border: 1px solid transparent;
        }
        .session-item:hover {
            background: #f0f0f0;
            border-color: #ddd;
        }
        .session-item.selected {
            background: #e3f2fd;
            border-color: #1976d2;
        }
        </style>
        """, unsafe_allow_html=True)

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
                    st.rerun()
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

def show_profile_modal():
    if st.session_state.get("show_profile", False):
        profile_container = st.empty()
        with profile_container.container():
            st.markdown("""
            <div class="profile-modal">
                <h3>👤 Profile</h3>
                <div class="profile-info">
            """, unsafe_allow_html=True)
            
            st.write(f"**USER NAME:** {st.session_state.username}")
            st.write(f"**EMAIL:** {st.session_state.email}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Edit Profile", key="edit_profile_btn"):
                    st.session_state.edit_profile = True
            with col2:
                if st.button("Close", key="close_profile_btn"):
                    st.session_state.show_profile = False
                    st.session_state.edit_profile = False
                    st.rerun()
            
            st.markdown("</div></div>", unsafe_allow_html=True)

    if st.session_state.get("edit_profile", False):
        edit_container = st.empty()
        with edit_container.container():
            st.markdown('<div class="profile-modal">', unsafe_allow_html=True)
            st.markdown("### Edit Profile")
            
            with st.form("profile_form"):
                new_username = st.text_input("Username", st.session_state.username)
                new_email = st.text_input("Email", st.session_state.email)
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("Update")
                with col2:
                    cancelled = st.form_submit_button("Cancel")
                
                if submitted:
                    success = update_user_profile(st.session_state.user_id, new_username, new_email)
                    if success:
                        st.success("Profile updated successfully!")
                        st.session_state.username = new_username
                        st.session_state.email = new_email
                        st.session_state.edit_profile = False
                        st.session_state.show_profile = False
                        st.rerun()
                    else:
                        st.error("Failed to update profile.")
                
                if cancelled:
                    st.session_state.edit_profile = False
                    st.session_state.show_profile = False
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

def render_chat_message(message, idx):
    """Render individual chat message with actions"""
    is_user = message["role"] == "user"
    message_class = "user-message" if is_user else "assistant-message"
    
    timestamp_str = format_timestamp(message.get('timestamp', datetime.utcnow()))
    
    st.markdown(f"""
    <div class="chat-message {message_class}">
        <div class="message-content">{message['content']}</div>
        <div class="chat-timestamp">{timestamp_str}</div>
        {'' if is_user else f'''
        <div class="message-actions">
            <button class="action-btn" onclick="navigator.clipboard.writeText('{message['content'].replace("'", "//'")}')">📋</button>
        </div>
        '''}
    </div>""", unsafe_allow_html=True)
    
    # Add action buttons for assistant messages
    if not is_user:
        col1, col2, col3 = st.columns([0.9, 0.05, 0.05])
        with col2:
            if st.button("👍", key=f"like_{idx}", help="Like"):
                update_feedback(message.get("id"), "like")
                st.toast("Feedback recorded!")
        with col3:
            if st.button("👎", key=f"dislike_{idx}", help="Dislike"):
                update_feedback(message.get("id"), "dislike")
                st.toast("Feedback recorded!")

def render_session_list():
    """Render session list with better styling"""
    try:
        sessions = get_user_chat_sessions(st.session_state.user_id)
        if sessions:
            st.markdown("### 💬 Chat History")
            
            # Create session selection
            for idx, session in enumerate(sessions):
                is_selected = st.session_state.current_session_id == session.id
                session_class = "session-item selected" if is_selected else "session-item"
                
                session_date = session.created_at.strftime('%Y-%m-%d %H:%M')
                session_preview = session.session_name[:50] + "..." if len(session.session_name) > 50 else session.session_name
                
                if st.button(
                    f"{session_preview}",
                    key=f"session_{session.id}",
                    help=f"Created: {session_date}",
                    use_container_width=True
                ):
                    load_session(session)
        else:
            st.info("No past conversations available.")
    except Exception as e:
        logger.error(f"Error loading chat sessions: {str(e)}")
        st.error("Failed to load chat sessions.")

def load_session(session):
    """Load a specific chat session"""
    if st.session_state.current_session_id != session.id:
        st.session_state.current_session_id = session.id
        st.session_state.current_session_name = session.session_name
        
        with st.spinner("Loading conversation..."):
            st.session_state.messages = []
            chatbot = get_chatbot()
            chatbot.reset_memory(str(st.session_state.user_id), str(session.id))
            chatbot.load_conversation_history(st.session_state.user_id, session.id)
            
            session_messages = get_session_chat_history(session.id)
            for message in session_messages:
                st.session_state.messages.append({
                    "role": "user",
                    "content": message.user_message,
                    "timestamp": message.timestamp,
                    "id": message.id
                })
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": message.bot_response,
                    "timestamp": message.timestamp,
                    "id": message.id
                })
        st.rerun()

def chat_interface():
    chatbot = get_chatbot()

    # Sidebar
    with st.sidebar:
        st.title(f"Welcome, {st.session_state.username}! 👋")
        
        st.markdown("---")
        
        # Session management
        render_session_list()
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🆕 New Chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.current_session_id = None
                st.session_state.current_session_name = None
                st.rerun()
        
        with col2:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.clear()
                st.rerun()

        # Profile button - hide when profile is shown
        if not st.session_state.get("show_profile", False) and not st.session_state.get("edit_profile", False):
            if st.button("👤 Profile", key="profile_btn", use_container_width=True):
                st.session_state.show_profile = True
                st.rerun()

        # Show profile modal
        show_profile_modal()

    # Main chat interface
    st.title("🤖 LangChain Hugging Face Chatbot")
    
    if st.session_state.current_session_name:
        st.caption(f"Current session: {st.session_state.current_session_name}")
    
    st.markdown("---")

    # Chat messages container
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
        for idx, message in enumerate(st.session_state.get("messages", [])):
            render_chat_message(message, idx)
        st.markdown('</div>', unsafe_allow_html=True)

    # Fixed input section at bottom
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    # File upload section
    uploaded_file = st.file_uploader(
        "📎 Attach file", 
        type=["txt", "pdf", "docx"], 
        key="file_upload",
        help="Upload a document to discuss"
    )
    
    # Input and send section
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        user_input = st.text_input(
            "Type your message here...", 
            key="chat_input",
            placeholder="Ask me anything...",
            label_visibility="collapsed"
        )
    with col2:
        send_clicked = st.button("➤", key="send_btn", help="Send", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Handle file upload
    if uploaded_file:
        file_content = process_uploaded_file(uploaded_file)
        if file_content and file_content != "Error processing file.":
            user_input = f"[File: {uploaded_file.name}]\n\n{file_content}"
            st.success(f"File '{uploaded_file.name}' processed successfully!")

    # Handle message submission
    if user_input and (send_clicked or st.session_state.get("auto_send", False)):
        process_user_message(user_input, chatbot)

def process_user_message(user_input, chatbot):
    """Process user message and generate response"""
    user_input = sanitize_input(user_input)
    
    # Add user message
    user_message = {
        "role": "user", 
        "content": user_input, 
        "timestamp": datetime.utcnow()
    }
    st.session_state.messages.append(user_message)
    
    # Create new session if needed
    if st.session_state.current_session_id is None:
        with get_db() as db:
            new_session = ChatSession(
                user_id=st.session_state.user_id,
                session_name=user_input[:100],  # Limit session name length
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            st.session_state.current_session_id = new_session.id
            st.session_state.current_session_name = user_input[:100]

    # Generate bot response
    with st.spinner("🤔 Thinking..."):
        try:
            bot_response = chatbot.get_response(
                user_input,
                str(st.session_state.user_id),
                str(st.session_state.current_session_id)
            )
            bot_response = sanitize_input(bot_response)
            
            # Save to database
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
                db.refresh(chat_entry)
                msg_id = chat_entry.id

            # Add bot message
            bot_message = {
                "role": "assistant",
                "content": bot_response,
                "timestamp": datetime.utcnow(),
                "id": msg_id
            }
            st.session_state.messages.append(bot_message)
            
            # Clear input
            st.session_state.chat_input = ""
            
        except Exception as e:
            logger.error(f"Error in chat processing: {str(e)}")
            st.error("⚠️ An error occurred while processing your message. Please try again.")
    
    st.rerun()

def main():
    if not st.session_state.authenticated:
        login_form()
    else:
        chat_interface()

if __name__ == "__main__":
    main()
