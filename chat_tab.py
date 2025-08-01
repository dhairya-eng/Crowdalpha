# chat_tab.py - CrowdAlpha | AI Command Chat Agent

import streamlit as st
import re
import google.generativeai as genai

# --- Gemini Config (temporary: swap later with your preferred LLM) ---
genai.configure(api_key="AIzaSyBx2OYyRBORpmQaKGYIV9J9LlVLYoEoYBw")
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
def render_chat_tab():
    st.header("💬 AI Command Agent")
    st.markdown("""
    Type commands like:
    - `/analyze TSLA`
    - `/compare NVDA AMD`
    - `/thesis AAPL`

    We'll generate a smart response using AI.
    """)

    command = st.text_input("Enter command:", value="/analyze TSLA", key="chat_command_input")

    if command:
        with st.spinner("Analyzing..."):
            prompt = f"""
    You are an AI assistant for a financial research terminal. Interpret the following command and return a concise report:

    Command:
    {command}

    Output should be structured clearly using markdown.
    """
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text.strip())
            except Exception as e:
                st.error(f"LLM Error: {e}")
