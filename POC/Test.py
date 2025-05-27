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
        # Use a unique key based on message count to force recreation
        input_key = f"chat_input_{len(st.session_state.get('messages', []))}"
        user_input = st.text_input(
            "Type your message here...", 
            key=input_key,
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
    if user_input and send_clicked:
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
            
            # DO NOT try to clear the input - let the rerun handle it with new key
            
        except Exception as e:
            logger.error(f"Error in chat processing: {str(e)}")
            st.error("⚠️ An error occurred while processing your message. Please try again.")
    
    st.rerun()
