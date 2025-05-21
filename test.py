/* Main styles for the LangChain Hugging Face Chatbot - Claude-like Design */

/* Global styles */
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background-color: #FFFFFF;
    color: #1A1A1A;
}

/* Update the Streamlit page layout */
.stApp {
    max-width: 100% !important; /* Change from fixed 760px to full width */
    padding: 0 !important;
}

/* Keep sidebar on the left */
.sidebar .sidebar-content {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    width: 250px; /* Adjust width as needed */
    overflow-y: auto;
    background-color: #F9FAFB;
    padding: 1rem;
    border-right: 1px solid #E5E7EB;
    z-index: 99;
}

/* Center the chat container but leave space for sidebar */
.main .block-container {
    max-width: 760px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* Header styling */
h1, h2, h3 {
    color: #1A1A1A;
    font-weight: 600;
}

h1 {
    font-size: 1.5rem !important;
    margin-bottom: 1.5rem !important;
}

/* Chat container */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    padding-bottom: 100px; /* Space for input box */
}

/* Chat message styling */
.chat-message {
    padding: 1rem 1.25rem;
    border-radius: 0.75rem;
    max-width: 85%;
    line-height: 1.5;
    font-size: 1rem;
    overflow-wrap: break-word;
}

.user-message {
    background-color: #F0F4F9;
    color: #1A1A1A;
    align-self: flex-end;
    margin-left: auto;
    border-bottom-right-radius: 0.25rem;
}

.bot-message {
    background-color: #FFFFFF;
    color: #1A1A1A;
    align-self: flex-start;
    border: 1px solid #E5E7EB;
    border-bottom-left-radius: 0.25rem;
}

/* Chat input area - fixed at bottom and centered properly */
.chat-input-container {
    position: fixed;
    bottom: 0;
    left: calc(50% + 125px); /* Account for sidebar by shifting right */
    transform: translateX(-50%);
    width: 760px; /* Fixed width matching chat area */
    max-width: calc(100% - 300px); /* Give room for sidebar */
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

.stTextInput > div {
    padding: 0;
    width: 100% !important;
}

.stTextInput > div > div {
    border-radius: 0.75rem !important;
    border-color: #E5E7EB !important;
    background-color: #FFFFFF !important;
    width: 100% !important;
}

/* Make sure columns are properly sized */
.row-widget.stHorizontal {
    width: 100% !important;
    max-width: 100% !important;
}

.stTextInput input {
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    color: #1A1A1A !important;
}

.stTextInput input:focus {
    box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2) !important;
    border-color: #6366F1 !important;
}

.stButton > button {
    background-color: #6366F1 !important;
    color: white !important;
    border: none !important;
    border-radius: 0.5rem !important;
    padding: 0.6rem 1.25rem !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: background-color 0.2s ease !important;
}

.stButton > button:hover {
    background-color: #4F46E5 !important;
}

/* Hide Streamlit branding */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

/* Chat history sidebar styling */
.sidebar h2 {
    font-size: 1.1rem;
    margin-bottom: 1rem;
}

.chat-history-item {
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;
    margin-bottom: 0.5rem;
    cursor: pointer;
    font-size: 0.875rem;
    color: #4B5563;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: background-color 0.2s ease;
}

.chat-history-item:hover {
    background-color: #F3F4F6;
    color: #1F2937;
}

.chat-history-item.active {
    background-color: #EEF2FF;
    color: #4F46E5;
    font-weight: 500;
}

/* Tab navigation - Claude style */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background-color: transparent;
    border-bottom: 1px solid #E5E7EB;
}

.stTabs [data-baseweb="tab"] {
    height: auto;
    padding: 0.75rem 1rem;
    font-size: 0.9rem;
    font-weight: 500;
    color: #6B7280;
    background-color: transparent;
    border: none;
    border-bottom: 2px solid transparent;
}

.stTabs [aria-selected="true"] {
    background-color: transparent;
    border-bottom: 2px solid #6366F1;
    color: #4F46E5;
}

/* Code blocks */
pre {
    background-color: #F9FAFB;
    border-radius: 0.5rem;
    padding: 1rem;
    overflow-x: auto;
    margin: 1rem 0;
    border: 1px solid #E5E7EB;
}

code {
    font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
    font-size: 0.875rem;
}

/* Slider styling */
.stSlider [data-baseweb="slider"] {
    max-width: 300px;
}

.stSlider [data-baseweb="thumb"] {
    background-color: #6366F1 !important;
}

.stSlider [data-baseweb="track-highlight"] {
    background-color: #6366F1 !important;
}

/* Fix for chat height to allow scrolling */
.main-content {
    height: calc(100vh - 180px);
    overflow-y: auto;
    padding-right: 10px;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #F9FAFB;
}

::-webkit-scrollbar-thumb {
    background-color: #D1D5DB;
    border-radius: 20px;
}

::-webkit-scrollbar-thumb:hover {
    background-color: #9CA3AF;
}

/* Responsive design */
@media screen and (max-width: 992px) {
    .chat-input-container {
        width: 80%;
        max-width: calc(100% - 250px);
        left: calc(50% + 125px); /* Adjust for sidebar */
    }
}

@media screen and (max-width: 768px) {
    .sidebar .sidebar-content {
        width: 200px;
    }
    
    .chat-input-container {
        width: 80%;
        max-width: calc(100% - 200px);
        left: calc(50% + 100px);
        padding: 0.75rem 1rem;
    }
    
    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    .chat-message {
        max-width: 90%;
    }
}

/* Smaller screens - collapsible sidebar */
@media screen and (max-width: 576px) {
    .sidebar .sidebar-content {
        width: 180px;
    }
    
    .chat-input-container {
        width: 80%;
        max-width: calc(100% - 180px);
        left: calc(50% + 90px);
    }
}
