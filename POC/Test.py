import html

def render_chat_message(message, idx):
    is_user = message["role"] == "user"
    message_class = "user-message" if is_user else "assistant-message"
    timestamp_str = format_timestamp(message.get('timestamp', datetime.utcnow()))
    
    # Escape content to avoid HTML breaking
    safe_content = html.escape(message['content'])
    
    # Compose HTML with minimal divs and escaped content
    html_content = f"""
    <div class="chat-message {message_class}">
        <div class="message-content">{safe_content}</div>
        <div class="chat-timestamp">{timestamp_str}</div>
        """
    if not is_user:
        # Inline copy button without extra div
        copy_text = message['content'].replace("'", "\\'")
        html_content += f"""
        <button class="action-btn" onclick="navigator.clipboard.writeText('{copy_text}')">📋</button>
        """
    html_content += "</div>"
    
    st.markdown(html_content, unsafe_allow_html=True)
