def render_chat_message(message, idx):
    """Render individual chat message with actions"""
    is_user = message["role"] == "user"
    message_class = "user-message" if is_user else "assistant-message"
    
    timestamp_str = format_timestamp(message.get('timestamp', datetime.utcnow()))
    
    # Create message container
    with st.container():
        if is_user:
            # User messages - no action buttons
            st.markdown(f"""
            <div class="chat-message {message_class}">
                <div class="message-content">{message['content']}</div>
                <div class="chat-timestamp">{timestamp_str}</div>
            </div>""", unsafe_allow_html=True)
        else:
            # Assistant messages - with action buttons
            col1, col2, col3, col4 = st.columns([0.85, 0.05, 0.05, 0.05])
            
            with col1:
                st.markdown(f"""
                <div class="chat-message {message_class}">
                    <div class="message-content">{message['content']}</div>
                    <div class="chat-timestamp">{timestamp_str}</div>
                </div>""", unsafe_allow_html=True)
            
            # Action buttons ONLY for assistant messages
            with col2:
                if st.button("📋", key=f"copy_{idx}", help="Copy to clipboard"):
                    st.session_state[f"copy_content_{idx}"] = message['content']
                    st.toast("Content copied to clipboard!")
            
            with col3:
                if st.button("👍", key=f"like_{idx}", help="Like this response"):
                    update_feedback(message.get("id"), "like")
                    st.toast("Feedback recorded!")
            
            with col4:
                if st.button("👎", key=f"dislike_{idx}", help="Dislike this response"):
                    update_feedback(message.get("id"), "dislike")
                    st.toast("Feedback recorded!")

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

    # Chat messages container with proper spacing
    chat_container = st.container()
    with chat_container:
        if st.session_state.get("messages", []):
            for idx, message in enumerate(st.session_state.messages):
                render_chat_message(message, idx)
        else:
            # Show welcome message when no messages
            st.markdown("""
            <div style="text-align: center; padding: 2rem; color: #666;">
                <h3>👋 Welcome to your AI Assistant!</h3>
                <p>Start a conversation by typing a message below.</p>
            </div>
            """, unsafe_allow_html=True)

    # Add some spacing before input
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Input section - use container instead of fixed positioning
    with st.container():
        st.markdown("---")
        
        # File upload section
        uploaded_file = st.file_uploader(
            "📎 Attach file", 
            type=["txt", "pdf", "docx"], 
            key=f"file_upload_{len(st.session_state.get('messages', []))}",
            help="Upload a document to discuss"
        )
        
        # Input and send section
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            # Use a unique key based on message count to force recreation
            input_key = f"chat_input_{len(st.session_state.get('messages', []))}"
            user_input = st.text_input(
                "Type your message here...", 
                key=input_key,
                placeholder="Ask me anything...",
                label_visibility="collapsed"
            )
        with col2:
            send_clicked = st.button("➤", key=f"send_btn_{len(st.session_state.get('messages', []))}", help="Send", use_container_width=True)

    # Handle file upload
    if uploaded_file:
        file_content = process_uploaded_file(uploaded_file)
        if file_content and file_content != "Error processing file.":
            user_input = f"[File: {uploaded_file.name}]\n\n{file_content}"
            st.success(f"File '{uploaded_file.name}' processed successfully!")

    # Handle message submission
    if user_input and send_clicked:
        process_user_message(user_input, chatbot)




def load_css():
    css_path = "styles/main.css"
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Improved CSS without fixed positioning issues
        st.markdown("""
        <style>
        /* Remove fixed positioning - let it flow naturally */
        .chat-messages {
            padding-bottom: 20px;
            min-height: 400px;
        }
        
        .chat-message {
            margin: 15px 0;
            padding: 15px;
            border-radius: 15px;
            position: relative;
            max-width: 80%;
            word-wrap: break-word;
        }
        
        .user-message {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
            margin-right: 0;
            text-align: right;
            border-bottom-right-radius: 5px;
        }
        
        .assistant-message {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            margin-left: 0;
            margin-right: auto;
            text-align: left;
            border-bottom-left-radius: 5px;
        }
        
        .message-content {
            margin-bottom: 8px;
            line-height: 1.6;
            font-size: 14px;
        }
        
        .chat-timestamp {
            font-size: 0.75em;
            opacity: 0.8;
            font-style: italic;
        }
        
        .user-message .chat-timestamp {
            color: rgba(255, 255, 255, 0.8);
        }
        
        .assistant-message .chat-timestamp {
            color: #6c757d;
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
        
        /* Styling for action buttons */
        .stButton > button {
            height: 2.2rem;
            width: 2.2rem;
            border-radius: 50%;
            border: 1px solid #ddd;
            background: white;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            background: #f8f9fa;
            border-color: #999;
            transform: scale(1.05);
        }
        
        /* Input section styling */
        .stTextInput > div > div > input {
            border-radius: 25px;
            border: 2px solid #e9ecef;
            padding: 10px 15px;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        
        /* File uploader styling */
        .stFileUploader > div {
            border-radius: 10px;
            border: 2px dashed #e9ecef;
            padding: 10px;
        }
        
        /* Send button styling */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 50%;
            height: 2.5rem;
            width: 2.5rem;
            font-size: 1.2rem;
        }
        
        /* Ensure proper spacing */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)




