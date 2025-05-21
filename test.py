#db.py

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    session_name = Column(String)  # Will store the first question as session name
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    # Define relationship with ChatHistory
    messages = relationship("ChatHistory", back_populates="session", cascade="all, delete-orphan")

class ChatHistory(Base):
    # Add this line to existing model
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"))
    # Add this relationship
    session = relationship("ChatSession", back_populates="messages")

#chatbot.py
def save_conversation(self, user_id: int, user_message: str, bot_response: str, session_id: int = None) -> bool:
    try:
        with get_db() as db:
            # Calculate response time in milliseconds
            response_time = int(time.time() * 1000)
            
            chat_history = ChatHistory(
                user_id=user_id,
                session_id=session_id,  # Add session_id parameter
                user_message=user_message,
                bot_response=bot_response,
                response_time=response_time
            )
            db.add(chat_history)
            db.commit()
            logger.info(f"Conversation saved for user {user_id} in session {session_id}")
            return True
    except Exception as e:
        logger.error(f"Unexpected error saving conversation: {str(e)}")
        return False

#utils.py
def get_user_chat_sessions(user_id: int, max_sessions: int = 10):
    """Get chat sessions for a specific user."""
    try:
        with get_db() as db:
            sessions = db.query(ChatSession).filter(
                ChatSession.user_id == user_id
            ).order_by(ChatSession.created_at.desc()).limit(max_sessions).all()
            
            return sessions
    except Exception as e:
        logger.error(f"Error getting chat sessions: {str(e)}")
        return []


def format_chat_sessions(sessions: List[ChatSession]) -> List[str]:
    """Format chat sessions for display in the sidebar."""
    try:
        formatted_sessions = []
        for session in sessions:
            date_str = session.created_at.strftime("%m-%d %H:%M")
            # Use session name (first question)
            session_name = session.session_name
            if len(session_name) > 30:
                session_name = session_name[:30] + "..."
            formatted_sessions.append(f"{date_str}: {session_name}")
        return formatted_sessions
    except Exception as e:
        logger.error(f"Error formatting chat sessions: {str(e)}")
        return ["Error loading sessions"]


def get_session_chat_history(session_id: int) -> List[ChatHistory]:
    """Get chat history for a specific session."""
    try:
        with get_db() as db:
            history = db.query(ChatHistory).filter(
                ChatHistory.session_id == session_id
            ).order_by(ChatHistory.timestamp).all()
            return history
    except Exception as e:
        logger.error(f"Error getting session history: {str(e)}")
        return []

#app.py

# Add these lines to the required_vars dictionary
'current_session_id': None,
'current_session_name': None,

#add new chatbutton:

# Add this right below the logout button in the sidebar
if st.sidebar.button("New Chat", key="new_chat_button"):
    # Clear current messages but keep user logged in
    st.session_state.messages = []
    st.session_state.current_session_id = None
    st.session_state.current_session_name = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("Past Conversations")

# Get user chat sessions from database
try:
    sessions = get_user_chat_sessions(st.session_state.user_id)
    if sessions:
        formatted_sessions = format_chat_sessions(sessions)
        selected_session_idx = st.sidebar.radio(
            "Select a previous conversation:",
            range(len(formatted_sessions)),
            format_func=lambda i: formatted_sessions[i],
            key="chat_sessions_radio"
        )
        
        # If a session is selected, load that session
        if st.sidebar.button("Load Selected Chat"):
            session = sessions[selected_session_idx]
            st.session_state.current_session_id = session.id
            st.session_state.current_session_name = session.session_name
            
            # Load chat history for this session
            with st.spinner("Loading conversation..."):
                session_messages = get_session_chat_history(session.id)
                st.session_state.messages = []
                for message in session_messages:
                    st.session_state.messages.append({"role": "user", "content": message.user_message})
                    st.session_state.messages.append({"role": "assistant", "content": message.bot_response})
            st.rerun()
    else:
        st.sidebar.info("No past conversations available.")
except Exception as e:
    logger.error(f"Error loading chat sessions: {str(e)}")
    st.sidebar.error("Failed to load chat sessions.")



# Inside the if user_input: block, right before getting bot response
# Check if this is a new session
if st.session_state.current_session_id is None:
    try:
        # Create a new chat session with first message as the name
        with get_db() as db:
            new_session = ChatSession(
                user_id=st.session_state.user_id,
                session_name=user_input  # First question becomes session name
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            
            st.session_state.current_session_id = new_session.id
            st.session_state.current_session_name = user_input
            logger.info(f"Created new chat session {new_session.id} for user {st.session_state.user_id}")
    except Exception as e:
        logger.error(f"Error creating chat session: {str(e)}")

# Pass the session ID when getting bot response
future = executor.submit(get_response_sync, chatbot, user_input, st.session_state.user_id, st.session_state.current_session_id)


















