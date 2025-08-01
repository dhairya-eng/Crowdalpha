# streamlit_ui.py - Reddit Feed Tab (modularized)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from crowdalpha import fetch_reddit_posts, group_posts_by_ticker

def render_reddit_tab():
    st.set_page_config(page_title="CrowdAlpha | Trending Stock Insights", layout="wide")
    st.title("📈 CrowdAlpha - Reddit-Powered Stock Insights")

    # --- Fetch and Process Posts ---
    st.info("Fetching Reddit posts from r/stocks...")
    posts = fetch_reddit_posts()
    grouped = group_posts_by_ticker(posts)
    tickers = sorted(grouped.keys())

    # --- Sidebar Ticker Filter ---
    st.sidebar.title("📊 Filter and Insights")
    selected_ticker = st.sidebar.selectbox("Choose a stock ticker:", tickers)

    # --- Ticker Frequency Bar Chart ---
    ticker_counts = {k: len(v) for k, v in grouped.items() if k != "UNCATEGORIZED"}
    top_n = dict(sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    st.sidebar.markdown("### 🔥 Top Tickers")
    st.sidebar.bar_chart(top_n)

    # --- Export to CSV ---
    flat_data = []
    for t, posts in grouped.items():
        for post in posts:
            flat_data.append({
                'ticker': t,
                'title': post['title'],
                'url': post['url'],
                'summary': post.get('summary', ''),
                'sentiment': post.get('sentiment', '')
            })

    df = pd.DataFrame(flat_data)
    st.sidebar.download_button('📁 Download Results', df.to_csv(index=False), 'crowdalpha.csv')

    # --- Main Display ---
    st.subheader(f"Posts related to: {selected_ticker}")

    for post in grouped[selected_ticker]:
        st.markdown(f"### 🔗 [{post['title']}]({post['url']})")
        if post['selftext']:
            st.markdown(f"> {post['selftext'][:300]}...")
        else:
            st.markdown("*No post body available.*")

        # Display LLM-enhanced insights
        sentiment = post.get("sentiment", "neutral").lower()
        emoji = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}.get(sentiment, "❔")

        with st.expander(f"💬 {emoji} Sentiment: {sentiment.title()}"):
            summary = post.get("summary", "")
            if "LLM error" in summary or "invalid" in summary.lower():
                st.warning("⚠️ AI Summary could not be generated for this post.")
            else:
                st.markdown("**AI Summary:**")
                st.markdown(summary or "*No summary available.*")

        st.markdown("---")
