import streamlit as st
import terminal_tab
import new_tab
import streamlit_ui  # this is your Reddit tab
import chat_tab
import compare_tab
st.set_page_config(page_title="CrowdAlpha Terminal", layout="wide")

st.sidebar.title("📚 Navigation")
tab = st.sidebar.radio("Choose a view:", ["Reddit Feed", "Ticker Terminal", "News Flow","AI Chat","Compare"])

if tab == "Reddit Feed":
    streamlit_ui.render_reddit_tab()

elif tab == "Ticker Terminal":
    terminal_tab.render_terminal_tab()

elif tab == "News Flow":
    new_tab.render_new_tab()
    import chat_tab 
elif tab == "AI Chat":
    chat_tab.render_chat_tab()  
elif tab == "Compare":
    compare_tab.render_compare_tab()

