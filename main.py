import streamlit as st
from app.ui import upload_section

st.set_page_config(page_title="AI Onboarding Copilot", layout="wide")
st.title("🚀 Smart Onboarding & Compliance Copilot")

# Render upload section
upload_section()
