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

    # Input section with Claude-style file attachment
    with st.container():
        st.markdown("---")
        
        # Initialize file attachment state
        if 'show_file_uploader' not in st.session_state:
            st.session_state.show_file_uploader = False
        
        # Main input row with text input and send button
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            input_key = f"chat_input_{len(st.session_state.get('messages', []))}"
            user_input = st.text_input(
                "Type your message here...", 
                key=input_key,
                placeholder="Ask me anything...",
                label_visibility="collapsed"
            )
        with col2:
            send_clicked = st.button("➤", key=f"send_btn_{len(st.session_state.get('messages', []))}", help="Send", use_container_width=True)
        
        # File attachment row - positioned below text input
        col1, col2, col3 = st.columns([0.05, 0.85, 0.1])
        
        with col1:
            # Plus button for file attachment
            if st.button("➕", key=f"attach_btn_{len(st.session_state.get('messages', []))}", help="Attach file"):
                st.session_state.show_file_uploader = not st.session_state.show_file_uploader
                st.rerun()
        
        with col2:
            # Show file uploader when plus button is clicked
            uploaded_file = None
            if st.session_state.show_file_uploader:
                uploaded_file = st.file_uploader(
                    "Choose a file to attach", 
                    type=["txt", "pdf", "docx"], 
                    key=f"file_upload_{len(st.session_state.get('messages', []))}",
                    help="Upload a document to discuss",
                    label_visibility="collapsed"
                )
                
                # Show file info if file is selected
                if uploaded_file:
                    st.success(f"📎 {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        with col3:
            # Close file uploader button when it's open
            if st.session_state.show_file_uploader:
                if st.button("✕", key=f"close_attach_{len(st.session_state.get('messages', []))}", help="Close"):
                    st.session_state.show_file_uploader = False
                    st.rerun()

    # Handle file upload processing
    file_content = None
    if uploaded_file:
        file_content = process_uploaded_file(uploaded_file)
        if file_content and file_content != "Error processing file.":
            # Don't automatically add to user_input, let user send when ready
            pass

    # Handle message submission
    if user_input and send_clicked:
        # Include file content if file was uploaded
        final_message = user_input
        if uploaded_file and file_content and file_content != "Error processing file.":
            final_message = f"[File: {uploaded_file.name}]\n\n{file_content}\n\nUser Question: {user_input}"
        
        process_user_message(final_message, chatbot)
        
        # Reset file uploader state after sending
        st.session_state.show_file_uploader = False

# Updated CSS for better styling of the new attachment UI
def load_css():
    css_path = "styles/main.css"
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Enhanced CSS with Claude-style file attachment styling
        st.markdown("""
        <style>
        /* Chat message styling */
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
        
        /* Input styling */
        .stTextInput > div > div > input {
            border-radius: 25px;
            border: 2px solid #e9ecef;
            padding: 12px 20px;
            font-size: 14px;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        
        /* File attachment button styling */
        .stButton > button {
            border-radius: 50%;
            border: 1px solid #e9ecef;
            background: #f8f9fa;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .stButton > button:hover {
            background: #e9ecef;
            border-color: #adb5bd;
            transform: scale(1.05);
        }
        
        /* Plus button specific styling */
        .stButton > button:has-text("➕") {
            background: #667eea;
            color: white;
            border: none;
            width: 35px;
            height: 35px;
            font-size: 16px;
        }
        
        .stButton > button:has-text("➕"):hover {
            background: #5a6fd8;
        }
        
        /* Send button styling */
        .stButton > button:has-text("➤") {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 50%;
            height: 40px;
            width: 40px;
            font-size: 16px;
        }
        
        /* Close button styling */
        .stButton > button:has-text("✕") {
            background: #dc3545;
            color: white;
            border: none;
            width: 30px;
            height: 30px;
            font-size: 14px;
        }
        
        .stButton > button:has-text("✕"):hover {
            background: #c82333;
        }
        
        /* File uploader styling when shown */
        .stFileUploader {
            margin-top: 5px;
        }
        
        .stFileUploader > div {
            border: 2px dashed #dee2e6;
            border-radius: 10px;
            padding: 15px;
            background: #f8f9fa;
        }
        
        .stFileUploader > div:hover {
            border-color: #667eea;
            background: #f0f2ff;
        }
        
        /* Action buttons for messages */
        .stButton > button:has-text("📋"),
        .stButton > button:has-text("👍"),
        .stButton > button:has-text("👎") {
            height: 32px;
            width: 32px;
            border-radius: 50%;
            border: 1px solid #ddd;
            background: white;
            font-size: 14px;
        }
        
        /* Profile modal */
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
        
        /* Session items */
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
        
        /* Success message for file attachment */
        .stAlert > div {
            border-radius: 10px;
            border-left: 4px solid #28a745;
        }
        </style>
        """, unsafe_allow_html=True)
