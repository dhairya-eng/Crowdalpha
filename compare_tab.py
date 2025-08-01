# compare_tab.py - CrowdAlpha | Compare Two Stocks

import streamlit as st
import yfinance as yf
import pandas as pd

def render_compare_tab():
    st.header("🆚 Compare Stocks")
    st.markdown("Enter two stock tickers to compare key metrics and performance.")

    # --- Inputs ---
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        ticker1 = st.text_input("Ticker 1:", value="AAPL", key="ticker1")
    with col_input2:
        ticker2 = st.text_input("Ticker 2:", value="MSFT", key="ticker2")

    # --- Data Loading ---
    def get_ticker_data(symbol):
        t = yf.Ticker(symbol)
        info = t.info
        hist = t.history(period="1mo")
        return info, hist

    if ticker1 and ticker2:
        try:
            info1, hist1 = get_ticker_data(ticker1)
            info2, hist2 = get_ticker_data(ticker2)

            st.subheader("📈 30-Day Price Comparison")
            chart_data = pd.DataFrame({
                ticker1.upper(): hist1['Close'],
                ticker2.upper(): hist2['Close']
            })
            st.line_chart(chart_data)

            st.subheader("📊 Snapshot")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"### {ticker1.upper()}")
                st.markdown(f"**Name:** {info1.get('shortName', 'N/A')}")
                st.markdown(f"**Sector:** {info1.get('sector', 'N/A')}")
                st.markdown(f"**Market Cap:** {info1.get('marketCap', 'N/A'):,}")
                st.markdown(f"**P/E Ratio:** {info1.get('trailingPE', 'N/A')}")
                st.markdown(f"**52W Range:** {info1.get('fiftyTwoWeekLow', 'N/A')} - {info1.get('fiftyTwoWeekHigh', 'N/A')}")

            with col2:
                st.markdown(f"### {ticker2.upper()}")
                st.markdown(f"**Name:** {info2.get('shortName', 'N/A')}")
                st.markdown(f"**Sector:** {info2.get('sector', 'N/A')}")
                st.markdown(f"**Market Cap:** {info2.get('marketCap', 'N/A'):,}")
                st.markdown(f"**P/E Ratio:** {info2.get('trailingPE', 'N/A')}")
                st.markdown(f"**52W Range:** {info2.get('fiftyTwoWeekLow', 'N/A')} - {info2.get('fiftyTwoWeekHigh', 'N/A')}")

        except Exception as e:
            st.error(f"Error comparing tickers: {e}")
