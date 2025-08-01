# news_tab.py - CrowdAlpha | Headline News per Ticker

import streamlit as st
import feedparser
import urllib.parse
def render_new_tab():
    st.header("📰 Ticker News Flow")
    st.markdown("Type a stock ticker to view recent financial news from Yahoo Finance.")

    # --- Input Ticker ---
    ticker = st.text_input("Enter a stock ticker (e.g., TSLA, AAPL, NVDA):", value="AAPL", key="news_ticker_input")


    if ticker:
        query = urllib.parse.quote(ticker.upper())
        rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={query}&region=US&lang=en-US"
        feed = feedparser.parse(rss_url)

        st.subheader(f"🗞️ News for {ticker.upper()}")

        if not feed.entries:
            st.warning("No news found or feed unavailable.")
        else:
            for entry in feed.entries:
                st.markdown(f"### [{entry.title}]({entry.link})")
                if hasattr(entry, 'summary'):
                    st.markdown(f"> {entry.summary[:300]}...")
                st.markdown("---")
