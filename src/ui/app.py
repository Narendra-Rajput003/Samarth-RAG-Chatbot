
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import requests
import pandas as pd
import time
import re

from src.utils.security import sanitize_input
from src.config.settings import settings

# Page configuration
st.set_page_config(
    page_title="Samarth RAG Chatbot",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme animations and styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    /* Dark theme background */
    .main {
        background-color: #1a1a1a;
        color: #ffffff;
    }

    .stApp {
        background-color: #1a1a1a;
    }

    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 70vh;
        text-align: center;
        animation: fadeIn 1.5s ease-in;
        background-color: #1a1a1a;
    }

    .welcome-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        opacity: 0;
        animation: slideUp 1s ease-out 0.5s forwards;
    }

    .welcome-subtitle {
        font-size: 1.25rem;
        color: #a0aec0;
        margin-bottom: 2rem;
        opacity: 0;
        animation: slideUp 1s ease-out 0.7s forwards;
    }

    .typing-text {
        font-size: 1.1rem;
        color: #cbd5e0;
        margin-bottom: 2rem;
        min-height: 1.5rem;
        opacity: 0;
        animation: slideUp 1s ease-out 0.9s forwards;
    }

    .chat-container {
        animation: fadeIn 0.8s ease-in;
        background-color: #1a1a1a;
    }

    .chat-message {
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        animation: slideInMessage 0.3s ease-out;
    }

    .user-message {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        margin-left: 2rem;
    }

    .assistant-message {
        background: #2d3748;
        border: 1px solid #4a5568;
        color: #e2e8f0;
        margin-right: 2rem;
    }

    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }

    /* Dark theme for sidebar */
    .stSidebar {
        background-color: #2d3748;
        color: #e2e8f0;
    }

    .stSidebar .stMarkdown {
        color: #e2e8f0;
    }

    /* Dark theme for buttons */
    .stButton button {
        background-color: #4a5568;
        color: #e2e8f0;
        border: 1px solid #718096;
    }

    .stButton button:hover {
        background-color: #718096;
        color: #ffffff;
    }

    /* Dark theme for input */
    .stTextInput input {
        background-color: #2d3748;
        color: #e2e8f0;
        border: 1px solid #4a5568;
    }

    /* Dark theme for chat input */
    .stChatInput input {
        background-color: #2d3748 !important;
        color: #e2e8f0 !important;
        border: 1px solid #4a5568 !important;
    }

    /* Dark theme for captions */
    .stCaption {
        color: #a0aec0;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideInMessage {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .gradient-bg {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .llm-indicator {
        position: fixed;
        top: 1rem;
        right: 1rem;
        background: rgba(45, 55, 72, 0.9);
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        font-size: 0.875rem;
        color: #e2e8f0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(74, 85, 104, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# LLM indicator
llm_name = "Gemini 2.0 Flash"
st.markdown(f'<div class="llm-indicator">🤖 {llm_name}</div>', unsafe_allow_html=True)

def format_ai_response(response: str) -> str:
    """Format AI response for better readability in chat."""
    # Replace markdown headers with emojis
    response = re.sub(r'^\*\*(.+?)\*\*$', r'📊 \1', response, flags=re.MULTILINE)

    # Add emojis to key sections
    response = re.sub(r'(?i)agricultural production:', '🌾 Agricultural Production:', response)
    response = re.sub(r'(?i)climate data:', '🌤️ Climate Data:', response)
    response = re.sub(r'(?i)trend analysis:', '📈 Trend Analysis:', response)
    response = re.sub(r'(?i)policy analysis:', '📋 Policy Analysis:', response)
    response = re.sub(r'(?i)comparative analysis:', '⚖️ Comparative Analysis:', response)
    response = re.sub(r'(?i)correlation:', '🔗 Correlation:', response)

    # Format bullet points
    response = re.sub(r'^- \*\*(.+?)\*\*:', r'• **\1**:', response)
    response = re.sub(r'^-\s+', '• ', response)

    # Add visual separators for long responses
    lines = response.split('\n')
    formatted_lines = []
    for i, line in enumerate(lines):
        formatted_lines.append(line)
        # Add separator after major sections
        if (line.startswith('📊') or line.startswith('🌾') or line.startswith('🌤️') or
            line.startswith('📈') or line.startswith('📋') or line.startswith('⚖️')) and i > 0:
            formatted_lines.append('---')

    return '\n'.join(formatted_lines)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = True
if "welcome_text" not in st.session_state:
    st.session_state.welcome_text = ""

# Welcome screen
if st.session_state.show_welcome:
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-title">🌾 Samarth RAG</div>
        <div class="welcome-subtitle">Your Intelligent Agricultural Assistant</div>
        <div class="typing-text" id="typing-text"></div>
    </div>
    """, unsafe_allow_html=True)

    # Typing effect
    welcome_messages = [
        "Ask me anything about agriculture and climate...",
        "I can help with crop recommendations...",
        "Get insights on weather patterns...",
        "Discover sustainable farming practices..."
    ]

    if st.session_state.welcome_text == "":
        for i, message in enumerate(welcome_messages):
            placeholder = st.empty()
            full_text = ""

            for char in message:
                full_text += char
                placeholder.markdown(f'<div class="typing-text">{full_text}▊</div>', unsafe_allow_html=True)
                time.sleep(0.05)

            placeholder.markdown(f'<div class="typing-text">{full_text}</div>', unsafe_allow_html=True)
            if i < len(welcome_messages) - 1:
                time.sleep(1)

        st.session_state.welcome_text = "complete"

    # Start chat button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Chat", key="start_chat", use_container_width=True):
            st.session_state.show_welcome = False
            st.rerun()

# Chat interface
if not st.session_state.show_welcome:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    # Chat messages
    for message in st.session_state.messages:
        message_class = "user-message" if message["role"] == "user" else "assistant-message"
        st.markdown(f'<div class="chat-message {message_class}">{message["content"]}</div>',
                   unsafe_allow_html=True)

    # Chat input
    prompt = st.chat_input("Ask about agriculture, climate, policy analysis...", key="chat_input")

    if prompt:
        prompt = sanitize_input(prompt)

        # User message with better formatting
        st.markdown(f'<div class="chat-message user-message">{prompt}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Assistant response with enhanced formatting
        with st.spinner("🧠 Analyzing data sources..."):
            try:
                response = requests.post("http://localhost:8000/query", json={"question": prompt})
                if response.status_code == 200:
                    data = response.json()

                    # Format the response for better readability
                    formatted_response = format_ai_response(data["answer"])

                    st.markdown(f'<div class="chat-message assistant-message">{formatted_response}</div>',
                               unsafe_allow_html=True)
                    st.caption(f"🔬 Analysis powered by: {data['llm_used']}")
                    st.session_state.messages.append({"role": "assistant", "content": data["answer"]})
                else:
                    st.error(f"❌ Error: {response.text}")
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")


    st.markdown('</div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-header">📊 Chat Options</div>', unsafe_allow_html=True)

        if st.button("🏠 Back to Home", key="back_home"):
            st.session_state.show_welcome = True
            st.rerun()

        if st.button("💾 Export Chat", key="export_chat"):
            if st.session_state.messages:
                # Create DataFrame
                chat_data = []
                for msg in st.session_state.messages:
                    chat_data.append({
                        "timestamp": pd.Timestamp.now(),
                        "role": msg["role"],
                        "message": msg["content"]
                    })

                df = pd.DataFrame(chat_data)

                # Export functionality
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"chat_history_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_csv"
                )
            else:
                st.info("💬 No messages to export yet!")

        st.markdown("---")
        st.markdown(f"**Model:** {llm_name}")
        st.markdown(f"**Messages:** {len(st.session_state.messages)}")

# Run: PYTHONPATH=. streamlit run src/ui/app.py