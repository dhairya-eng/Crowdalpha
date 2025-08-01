# chat_tab.py - CrowdAlpha | AI Command Chat Agent (Groq + OpenRouter Fallback)

# import streamlit as st
# import os
# from dotenv import load_dotenv
# import openai

# # Load API keys from .env
# load_dotenv()
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# # Configure Groq client (primary)
# groq_client = openai.OpenAI(
#     api_key=GROQ_API_KEY,
#     base_url="https://api.groq.com/openai/v1"
# )

# # Configure OpenRouter client (fallback)
# openrouter_client = openai.OpenAI(
#     api_key=OPENROUTER_API_KEY,
#     base_url="https://openrouter.ai/api/v1"
# )

# def generate_ai_response(command: str) -> str:
#     """
#     Try Groq (LLaMA3-70B) first, fallback to OpenRouter (LLaMA3-8B).
#     """
#     prompt = f"""
#     You are an AI assistant for a financial research terminal. Interpret the following command
#     and return a concise, clear financial analysis with markdown formatting.

#     Command:
#     {command}
#     """

#     try:
#         # Primary: Groq
#         response = groq_client.chat.completions.create(
#             model="llama3-70b-8192",
#             messages=[{"role": "user", "content": prompt}]
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as groq_error:
#         st.warning(f"Groq API failed, falling back to OpenRouter: {groq_error}")
#         try:
#             response = openrouter_client.chat.completions.create(
#                 model="meta-llama/llama-3-8b-instruct:free",
#                 messages=[{"role": "user", "content": prompt}]
#             )
#             return response.choices[0].message.content.strip()
#         except Exception as openrouter_error:
#             st.error(f"Both LLM calls failed: {openrouter_error}")
#             return "⚠️ AI response unavailable."

# def render_chat_tab():
#     st.header("💬 AI Command Agent")
#     st.markdown("""
#     Type commands like:
#     - `/analyze TSLA`
#     - `/compare NVDA AMD`
#     - `/thesis AAPL`

#     We'll generate a smart response using AI (Groq → OpenRouter fallback).
#     """)

#     command = st.text_input("Enter command:", value="/analyze TSLA", key="chat_command_input")

#     if command:
#         with st.spinner("Analyzing..."):
#             result = generate_ai_response(command)
#             st.markdown(result)

# chat_tab.py - CrowdAlpha | AI Command Chat Agent (with /earnings support)

import streamlit as st
import os
from dotenv import load_dotenv
import openai
import requests
from bs4 import BeautifulSoup

# Load API keys
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Configure LLM clients
groq_client = openai.OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
openrouter_client = openai.OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")


def call_llm(prompt: str):
    """Try Groq first, then OpenRouter fallback."""
    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.warning(f"Groq failed, fallback to OpenRouter: {e}")
        try:
            response = openrouter_client.chat.completions.create(
                model="meta-llama/llama-3-8b-instruct:free",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"Both LLM calls failed: {e}")
            return "⚠️ AI response unavailable."


def fetch_earnings_transcript(ticker: str) -> str:
    """
    Fetches earnings transcript from Motley Fool as fallback demo.
    """
    url = f"https://www.fool.com/earnings-call-transcripts/{ticker.lower()}-earnings-call-transcript.aspx"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Motley Fool transcripts are inside <div class="article-content">
            content_div = soup.find("div", class_="article-content")
            paragraphs = content_div.find_all("p") if content_div else []
            transcript = "\n".join(p.get_text() for p in paragraphs)
            return transcript if transcript.strip() else "Transcript content unavailable."
        else:
            return "Transcript not available or ticker invalid."
    except Exception as e:
        return f"Error fetching transcript: {e}"



def handle_earnings_command(ticker: str) -> str:
    transcript = fetch_earnings_transcript(ticker)
    prompt = f"""
    Summarize the following earnings call transcript for {ticker} in bullet points:
    Include revenue, EPS, key themes, and sentiment (bullish/bearish/neutral).
    
    Transcript:
    {transcript}
    """
    return call_llm(prompt)


def generate_ai_response(command: str) -> str:
    """
    Handle AI chat commands, including /earnings.
    """
    if command.startswith("/earnings"):
        parts = command.split()
        if len(parts) < 2:
            return "⚠️ Please specify a ticker symbol. Example: `/earnings MSFT`"
        ticker = parts[1].upper()
        return handle_earnings_command(ticker)
    else:
        # Default AI response flow
        prompt = f"""
        You are an AI assistant for a financial research terminal. 
        Interpret the following command and return a concise, clear financial analysis with markdown formatting.
        
        Command:
        {command}
        """
        return call_llm(prompt)


def render_chat_tab():
    st.header("💬 AI Command Agent")
    st.markdown("""
    Type commands like:
    - `/analyze TSLA`
    - `/compare NVDA AMD`
    - `/thesis AAPL`
    - `/earnings MSFT (Under development)` 
    """)

    command = st.text_input("Enter command:", value="/earnings MSFT", key="chat_command_input")

    if command:
        with st.spinner("Analyzing..."):
            result = generate_ai_response(command)
            st.markdown(result)
