import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import subprocess

st.set_page_config(page_title="Stock Sentiment Dashboard", layout="wide")
st.title("📈 Stock Sentiment Dashboard")

# Load labeled JSON file if it exists
json_file = Path("news_labeled.json")

# User inputs stock symbol
user_ticker = st.text_input("🔍 Enter a stock symbol (e.g., TSLA, NVDA):").strip().upper()

# Button to trigger scraping
if st.button("🕷️ Scrape News and Analyze Sentiment"):
    if user_ticker:
        with st.spinner(f"Scraping and analyzing news for {user_ticker}..."):
            result = subprocess.run(["python3", "scraper.py"], input=user_ticker.encode(), capture_output=True)
            st.success("Scraping complete. You can now view the updated dashboard.")
            st.rerun()
    else:
        st.warning("Please enter a stock ticker before scraping.")

# Check if data exists
if not json_file.exists():
    st.warning("No data file found. Please scrape a stock to generate 'news_labeled.json'.")
    st.stop()

# Load data
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

if not user_ticker:
    st.info("Please enter a stock symbol to view sentiment-labeled news.")
    st.stop()

if user_ticker not in data:
    st.error(f"No data found for '{user_ticker}'. Please scrape this symbol first.")
    st.stop()

# Sidebar sentiment filter
sentiment_filter = st.sidebar.multiselect(
    "🧠 Filter by Sentiment", ["positive", "neutral", "negative"], default=["positive", "neutral", "negative"]
)

st.markdown(f"### 📰 News for `{user_ticker}`")

# Display articles
for url, article in data[user_ticker].items():
    sentiment = article.get("sentiment", "unknown")
    if sentiment not in sentiment_filter:
        continue

    title = article.get("title", url)
    score = article.get("score", 0)
    timestamp = article.get("timestamp", "Unknown")
    preview = article["text"][:500] + "..." if len(article["text"]) > 500 else article["text"]

    with st.expander(f"🕒 {timestamp} | 🧠 {sentiment.capitalize()} ({int(score*100)}%) | 🔗 {title}"):
        st.markdown(f"[Open Article]({url})", unsafe_allow_html=True)
        st.markdown(f"**Sentiment:** `{sentiment}`  \\n**Score:** `{score}`")
        st.markdown("**Preview:**")
        st.write(preview)
