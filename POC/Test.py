with st.container():
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    input_col, file_col, send_col = st.columns([7, 2, 1])
    with input_col:
        user_input = st.text_input("Your message", key="user_input", placeholder="Type your message here...")
    with file_col:
        uploaded_file = st.file_uploader("Attach file", key="file_uploader")
    with send_col:
        send_clicked = st.button("Send")
    st.markdown('</div>', unsafe_allow_html=True)

