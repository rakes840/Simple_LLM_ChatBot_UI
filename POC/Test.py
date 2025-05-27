import streamlit as st
import html
import json
from datetime import datetime

def format_timestamp(ts):
    return ts.strftime("%Y-%m-%d %H:%M")

def render_chat_message(message, idx):
    is_user = message["role"] == "user"
    message_class = "user-message" if is_user else "assistant-message"
    timestamp_str = format_timestamp(message.get('timestamp', datetime.utcnow()))
    safe_content = html.escape(message['content'])
    html_content = f"""
    <div class="chat-message {message_class}">
        <div class="message-content">{safe_content}</div>
        <div class="chat-timestamp">{timestamp_str}</div>
    """
    if not is_user:
        js_content = json.dumps(message['content'])
        html_content += f"""
        <div class="message-actions">
            <button class="action-btn" onclick="navigator.clipboard.writeText({js_content})">📋</button>
        </div>
        """
    html_content += "</div>"
    st.markdown(html_content, unsafe_allow_html=True)

messages = [
    {"role": "user", "content": "Hi <b>there</b>!"},
    {"role": "assistant", "content": "Hello! How can I help you? 'Copy' this <div>."}
]

for idx, msg in enumerate(messages):
    render_chat_message(msg, idx)
