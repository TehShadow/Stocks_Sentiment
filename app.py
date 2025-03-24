import streamlit as st
import json
from datetime import datetime

# Load labeled news data
with open("news_labeled.json", "r", encoding="utf-8") as f:
    data = json.load(f)

st.set_page_config(page_title="Stock Sentiment Dashboard", layout="wide")
st.title("📈 Stock Sentiment Dashboard")
st.markdown("View sentiment-labeled news stories by company.")

# Sidebar: stock selection + sentiment filter
tickers = list(data.keys())
selected_ticker = st.sidebar.selectbox("📊 Select Stock", tickers)
sentiment_filter = st.sidebar.multiselect("🧠 Filter by Sentiment", ["positive", "neutral", "negative"], default=["positive", "neutral", "negative"])

st.markdown(f"### 📰 News for `{selected_ticker}`")

# Show results
for url, article in data[selected_ticker].items():
    sentiment = article.get("sentiment", "unknown")
    if sentiment not in sentiment_filter:
        continue

    title = article.get("title", url)
    score = article.get("score", 0)
    timestamp = article.get("timestamp", "Unknown Date")
    preview = article["text"][:500] + "..." if len(article["text"]) > 500 else article["text"]

    with st.expander(f"🕒 {timestamp} | 🧠 {sentiment.capitalize()} ({int(score*100)}%) | 🔗 {title}"):
        st.markdown(f"[**Open Article**]({url})", unsafe_allow_html=True)
        st.markdown(f"**Sentiment:** `{sentiment}`  \n**Score:** `{score}`")
        st.markdown(f"**Published:** `{timestamp}`")
        st.markdown("**Preview:**")
        st.write(preview)