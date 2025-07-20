import streamlit as st
from app.ui import upload_section, chatbot_panel  

st.set_page_config(page_title="AI Onboarding Copilot", layout="wide")
st.title("🚀 Smart Onboarding & Compliance Copilot")

# Sidebar toggle for chatbot
if "chatbot_open" not in st.session_state:
    st.session_state.chatbot_open = False

if st.sidebar.button("🤖 Chatbot Assistant"):
    st.session_state.chatbot_open = not st.session_state.chatbot_open

# Render upload section
upload_section()

# Conditionally show chatbot
if st.session_state.chatbot_open:
    chatbot_panel()
