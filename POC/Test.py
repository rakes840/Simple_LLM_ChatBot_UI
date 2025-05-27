def render_chat_message(message, idx):
    """Render individual chat message with actions - Debug Version"""
    is_user = message["role"] == "user"
    message_class = "user-message" if is_user else "assistant-message"
    
    timestamp_str = format_timestamp(message.get('timestamp', datetime.utcnow()))
    
    # Debug: Print message details
    print(f"DEBUG - Message {idx}: Role = {message['role']}, Is_User = {is_user}")
    
    # Create message container
    with st.container():
        if is_user:
            # User messages - NO action buttons
            st.markdown(f"""
            <div class="chat-message {message_class}">
                <div class="message-content"><strong>You:</strong> {message['content']}</div>
                <div class="chat-timestamp">{timestamp_str}</div>
            </div>""", unsafe_allow_html=True)
            
            # Debug: Show what we detected
            st.caption(f"DEBUG: User message detected - NO buttons should show")
            
        else:
            # Assistant messages - WITH action buttons
            st.markdown(f"""
            <div class="chat-message {message_class}">
                <div class="message-content"><strong>Assistant:</strong> {message['content']}</div>
                <div class="chat-timestamp">{timestamp_str}</div>
            </div>""", unsafe_allow_html=True)
            
            # Debug: Show what we detected
            st.caption(f"DEBUG: Assistant message detected - Buttons should show")
            
            # Action buttons row
            col1, col2, col3, col4 = st.columns([0.82, 0.06, 0.06, 0.06])
            
            with col1:
                st.write("")  # Empty space
            
            # Action buttons ONLY for assistant messages
            with col2:
                if st.button("📋", key=f"copy_{idx}", help="Copy response to clipboard"):
                    st.session_state[f"copy_content_{idx}"] = message['content']
                    st.toast("Response copied to clipboard!")
            
            with col3:
                if st.button("👍", key=f"like_{idx}", help="Like this response"):
                    update_feedback(message.get("id"), "like")
                    st.toast("Positive feedback recorded!")
            
            with col4:
                if st.button("👎", key=f"dislike_{idx}", help="Dislike this response"):
                    update_feedback(message.get("id"), "dislike")
                    st.toast("Negative feedback recorded!")

# Also add this debug function to check your messages array
def debug_messages():
    """Debug function to check message structure"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("**DEBUG INFO:**")
    if st.session_state.get("messages"):
        for i, msg in enumerate(st.session_state.messages):
            role = msg.get("role", "unknown")
            content_preview = msg.get("content", "")[:30] + "..."
            st.sidebar.text(f"{i}: {role} - {content_preview}")
    else:
        st.sidebar.text("No messages found")

# Add this to your chat_interface function after the sidebar section:
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
        
        # ADD DEBUG INFO
        debug_messages()

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
