/* Chat input area - fixed at bottom and centered */
.chat-input-container {
    position: fixed;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 760px; /* Fixed width matching chat area */
    max-width: 80%; /* Limit width on smaller screens */
    margin-left: 125px; /* Half of sidebar width to offset the centering */
    background-color: #FFFFFF;
    padding: 1rem 2rem;
    border-top: 1px solid #E5E7EB;
    z-index: 100;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}

/* Make the input element itself have proper dimensions */
.stTextInput {
    max-width: 100% !important;
}

.stTextInput > div > div {
    width: 100% !important;
}
