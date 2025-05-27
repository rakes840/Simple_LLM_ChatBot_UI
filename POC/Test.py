def render_chat_message(message, idx):
    """Render individual chat message with actions"""
    is_user = message["role"] == "user"
    message_class = "user-message" if is_user else "assistant-message"
    
    timestamp_str = format_timestamp(message.get('timestamp', datetime.utcnow()))
    
    # Create message container
    with st.container():
        # Display message content with proper styling
        if is_user:
            st.markdown(f"""
            <div class="chat-message {message_class}">
                <div class="message-content">{message['content']}</div>
                <div class="chat-timestamp">{timestamp_str}</div>
            </div>""", unsafe_allow_html=True)
        else:
            # For assistant messages, create columns for content and actions
            col1, col2, col3, col4 = st.columns([0.85, 0.05, 0.05, 0.05])
            
            with col1:
                st.markdown(f"""
                <div class="chat-message {message_class}">
                    <div class="message-content">{message['content']}</div>
                    <div class="chat-timestamp">{timestamp_str}</div>
                </div>""", unsafe_allow_html=True)
            
            # Action buttons using Streamlit buttons instead of HTML/JS
            with col2:
                if st.button("📋", key=f"copy_{idx}", help="Copy to clipboard"):
                    # Store content in session state for copying
                    st.session_state[f"copy_content_{idx}"] = message['content']
                    st.toast("Content copied to clipboard!")
            
            with col3:
                if st.button("👍", key=f"like_{idx}", help="Like"):
                    update_feedback(message.get("id"), "like")
                    st.toast("Feedback recorded!")
            
            with col4:
                if st.button("👎", key=f"dislike_{idx}", help="Dislike"):
                    update_feedback(message.get("id"), "dislike")
                    st.toast("Feedback recorded!")



def load_css():
    css_path = "styles/main.css"
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Inline CSS as fallback - removed JavaScript-dependent styles
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
        .chat-message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 10px;
            position: relative;
        }
        .user-message {
            background: #e3f2fd;
            margin-left: 20%;
            text-align: right;
        }
        .assistant-message {
            background: #f5f5f5;
            margin-right: 20%;
            text-align: left;
        }
        .message-content {
            margin-bottom: 5px;
            line-height: 1.5;
        }
        .chat-timestamp {
            font-size: 0.8em;
            color: #666;
            opacity: 0.7;
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
        /* Streamlit button styling for action buttons */
        .stButton > button {
            height: 2rem;
            width: 2rem;
            border-radius: 50%;
            border: 1px solid #ddd;
            background: white;
            font-size: 0.8rem;
        }
        .stButton > button:hover {
            background: #f0f0f0;
            border-color: #999;
        }
        </style>
        """, unsafe_allow_html=True)


