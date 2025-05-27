import html
import json

def render_chat_message(message, idx):
    is_user = message["role"] == "user"
    message_class = "user-message" if is_user else "assistant-message"
    timestamp_str = format_timestamp(message.get('timestamp', datetime.utcnow()))
    
    # Escape HTML special characters in message content
    safe_content = html.escape(message['content'])
    
    # Use json.dumps to safely encode the content for JS string literal
    js_content = json.dumps(message['content'])
    
    # Compose HTML safely
    html_content = f"""
    <div class="chat-message {message_class}">
        <div class="message-content">{safe_content}</div>
        <div class="chat-timestamp">{timestamp_str}</div>
    """
    if not is_user:
        html_content += f"""
        <div class="message-actions">
            <button class="action-btn" onclick="navigator.clipboard.writeText({js_content})">📋</button>
        </div>
        """
    html_content += "</div>"
    
    st.markdown(html_content, unsafe_allow_html=True)
    
    # Optional: Add Streamlit buttons for feedback (like/dislike)
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
