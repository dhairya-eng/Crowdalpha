# terminal_tab.py - CrowdAlpha | Ticker Terminal View

import streamlit as st
import yfinance as yf
import pandas as pd

def render_terminal_tab():
    # --- Header ---
    st.header("📊 Ticker Terminal")
    st.markdown("Type a stock ticker below to explore recent performance and company info.")

    # --- Ticker Input ---
    ticker_input = st.text_input("Enter a stock ticker (e.g., TSLA, AAPL, NVDA):", value="AAPL", key="terminal_ticker_input")


    if ticker_input:
        try:
            ticker = yf.Ticker(ticker_input.upper())
            info = ticker.info
            hist = ticker.history(period="1mo")

            # --- Price Overview ---
            st.subheader(f"📈 Price Performance: {ticker_input.upper()}")
            st.line_chart(hist['Close'])

            # --- Company Overview ---
            st.subheader("🏢 Company Snapshot")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Name:** {info.get('shortName', 'N/A')}")
                st.markdown(f"**Sector:** {info.get('sector', 'N/A')}")
                st.markdown(f"**Industry:** {info.get('industry', 'N/A')}")
                st.markdown(f"**Country:** {info.get('country', 'N/A')}")
            with col2:
                st.markdown(f"**Market Cap:** {info.get('marketCap', 'N/A'):,}")
                st.markdown(f"**P/E Ratio:** {info.get('trailingPE', 'N/A')}")
                st.markdown(f"**52W Range:** {info.get('fiftyTwoWeekLow', 'N/A')} - {info.get('fiftyTwoWeekHigh', 'N/A')}")
                st.markdown(f"**Dividend Yield:** {info.get('dividendYield', 'N/A')}")

            # --- Description ---
            st.subheader("📝 Description")
            st.markdown(info.get('longBusinessSummary', 'No description available.'))

        except Exception as e:
            st.error(f"Error loading ticker data: {e}")
