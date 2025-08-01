# CrowdAlpha - MVP Backend (OpenRouter + Mistral + LLM Caching)

import praw
import re
import time
import json
import os
import hashlib
from collections import defaultdict
from openai import OpenAI

# --- CONFIGURATION ---
REDDIT_CLIENT_ID = 'tD7Dcx6DzND4BituUe3LWA'
REDDIT_CLIENT_SECRET = 'N7z-THlJQOc19wWTnZXXhbv7KohxKw'
REDDIT_USER_AGENT = 'CrowdAlphaBot/0.1'
OPENROUTER_API_KEY = "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"
CACHE_FILE = "llm_cache.json"

# --- INIT ---
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# --- Load or Init Cache ---
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        llm_cache = json.load(f)
else:
    llm_cache = {}

# --- Regex to Extract Potential Tickers (e.g., $TSLA, NVDA) ---
TICKER_REGEX = r'\b[A-Z]{2,5}\b|\$[A-Z]{1,5}\b'

# --- Hash helper ---
def get_post_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()


# --- Scrape Top Posts ---
def fetch_reddit_posts(subreddit="stocks", limit=10):
    posts = []
    for submission in reddit.subreddit(subreddit).hot(limit=limit):
        if not submission.stickied and len(submission.title) > 15:
            posts.append({
                "title": submission.title,
                "selftext": submission.selftext,
                "url": submission.url
            })
    return posts


# --- LLM Extraction with Caching using Mistral ---
def extract_thesis_from_post(text):
    prompt = f"""
You are a financial analyst AI. Read the Reddit post below and extract a JSON object with:
- A list of stock tickers mentioned (e.g., [\"TSLA\", \"NVDA\"])
- A sentiment (bullish, bearish, neutral)
- A few short reasons explaining the sentiment

Reddit Post:
\"\"\"{text}\"\"\"

Respond ONLY with valid JSON in this format:
{{
  "ticker": [...],
  "sentiment": "bullish/bearish/neutral",
  "reason": ["...", "..."]
}}
    """

    post_id = get_post_hash(text)
    if post_id in llm_cache:
        return llm_cache[post_id]

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct:free",
            extra_headers={
                "HTTP-Referer": "https://yourappname.streamlit.app",
                "X-Title": "CrowdAlpha"
            },
            messages=[
                {"role": "system", "content": "You are a financial analyst assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        raw = response.choices[0].message.content.strip()
        print("\n[OpenRouter RAW OUTPUT]:", raw)

        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            result = json.loads(match.group(0))
            llm_cache[post_id] = result
            with open(CACHE_FILE, "w") as f:
                json.dump(llm_cache, f, indent=2)
            return result

        raise ValueError("No valid JSON object found in LLM output")

    except Exception as e:
        print("OpenRouter Error:", e)
        return {
            "ticker": [],
            "sentiment": "neutral",
            "reason": ["LLM error or invalid response format"]
        }

# --- Extract Tickers from Text (fallback or for cross-checking) ---
def extract_tickers(text):
    tickers = re.findall(TICKER_REGEX, text.upper())
    clean = [t.replace('$', '') for t in tickers if len(t.replace('$', '')) <= 5]
    return list(set(clean))


# --- Group Posts by Ticker ---
def group_posts_by_ticker(posts):
    grouped = defaultdict(list)
    for post in posts:
        full_text = post['title'] + "\n" + post['selftext']
        llm_result = extract_thesis_from_post(full_text)
        time.sleep(60)# prevent rate limit bursts

        tickers = llm_result.get("ticker") or extract_tickers(full_text)
        if not tickers:
            tickers = ["UNCATEGORIZED"]

        for ticker in tickers:
            post["summary"] = "; ".join(llm_result.get("reason", []))
            post["sentiment"] = llm_result.get("sentiment", "neutral")
            grouped[ticker].append(post)
    return grouped


# --- Display Grouped Posts ---
def display_grouped_posts(grouped):
    for ticker, posts in grouped.items():
        print(f"\n=== {ticker} ===")
        for post in posts:
            print(f"- {post['title'][:100]}")


# --- Run Script ---
def run():
    posts = fetch_reddit_posts()
    grouped = group_posts_by_ticker(posts)
    display_grouped_posts(grouped)

if __name__ == '__main__':
    run()
