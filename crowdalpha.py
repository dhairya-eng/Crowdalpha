# crowdalpha.py - CrowdAlpha | Parallel Reddit Sentiment with Groq + OpenRouter Fallback

import praw
import re
import time
import json
import os
import hashlib
import concurrent.futures
from collections import defaultdict
from dotenv import load_dotenv
import openai

# --- Load Environment ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# --- Reddit Config ---
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "CrowdAlphaBot/0.2")

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

# --- LLM Clients ---
groq_client = openai.OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
openrouter_client = openai.OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

# --- Cache File ---
CACHE_FILE = "llm_cache.json"
llm_cache = json.load(open(CACHE_FILE)) if os.path.exists(CACHE_FILE) else {}

# --- Regex for Tickers ---
TICKER_REGEX = r"\b[A-Z]{2,5}\b|\$[A-Z]{1,5}\b"


def get_post_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def extract_tickers(text):
    tickers = re.findall(TICKER_REGEX, text.upper())
    return list(set([t.replace("$", "") for t in tickers if len(t) <= 5]))


def call_llm(prompt: str):
    """Try Groq first, then fallback to OpenRouter."""
    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Groq failed, fallback to OpenRouter:", e)
        try:
            response = openrouter_client.chat.completions.create(
                model="meta-llama/llama-3-8b-instruct:free",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print("Both LLM calls failed:", e)
            return '{"ticker": [], "sentiment": "neutral", "reason": ["LLM error"]}'


def extract_thesis_from_post(text):
    """
    Analyze Reddit post to extract ticker, sentiment, and reasons.
    Uses cache to avoid repeated calls.
    """
    post_id = get_post_hash(text)
    if post_id in llm_cache:
        return llm_cache[post_id]

    prompt = f"""
    You are a financial analyst AI. Read the Reddit post below and extract JSON:
    {{
      "ticker": ["TICKER1","TICKER2"],
      "sentiment": "bullish/bearish/neutral",
      "reason": ["reason1","reason2"]
    }}
    Post:
    \"\"\"{text}\"\"\"
    """

    raw = call_llm(prompt)

    # Extract JSON safely
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group(0))
        except json.JSONDecodeError:
            result = {"ticker": [], "sentiment": "neutral", "reason": ["JSON parse error"]}
    else:
        result = {"ticker": [], "sentiment": "neutral", "reason": ["Invalid LLM output"]}

    # Cache result
    llm_cache[post_id] = result
    json.dump(llm_cache, open(CACHE_FILE, "w"), indent=2)
    return result


def fetch_reddit_posts(subreddit="stocks", limit=10):
    posts = []
    try:
        for submission in reddit.subreddit(subreddit).hot(limit=limit):
            if not submission.stickied and len(submission.title) > 15:
                posts.append({
                    "title": submission.title,
                    "selftext": submission.selftext or "",
                    "url": submission.url
                })
    except Exception as e:
        print(f"Error fetching Reddit posts: {e}")
    return posts


def process_post(post):
    """Process one Reddit post (parallel safe)."""
    full_text = post['title'] + "\n" + post['selftext']
    llm_result = extract_thesis_from_post(full_text)
    tickers = llm_result.get("ticker") or extract_tickers(full_text)
    if not tickers:
        tickers = ["UNCATEGORIZED"]

     # Filter out "unknown" or placeholder reasons
    reasons = [
        r for r in llm_result.get("reason", [])
        if r and r.lower() not in ["unknown", "n/a", "none"]
    ]
    summary = "; ".join(reasons) if reasons else "No clear reason provided by AI."

    for ticker in tickers:
        yield ticker, {
            "title": post['title'],
            "selftext": post['selftext'],
            "url": post['url'],
            "summary": summary,
            "sentiment": llm_result.get("sentiment", "neutral")
        }


def group_posts_by_ticker(posts):
    grouped = defaultdict(list)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_post, post) for post in posts]
        for future in concurrent.futures.as_completed(futures):
            try:
                for ticker, processed_post in future.result():
                    grouped[ticker].append(processed_post)
            except Exception as e:
                print(f"Error processing post: {e}")
    return grouped


def display_grouped_posts(grouped):
    """For CLI testing (optional)."""
    for ticker, posts in grouped.items():
        print(f"\n=== {ticker} ===")
        for post in posts:
            print(f"- {post['title'][:100]}")


def run():
    posts = fetch_reddit_posts()
    grouped = group_posts_by_ticker(posts)
    display_grouped_posts(grouped)


if __name__ == "__main__":
    run()
