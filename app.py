import streamlit as st
import json

# Load the labeled news
with open("news_labeled.json", "r", encoding="utf-8") as f:
    data = json.load(f)

st.set_page_config(page_title="Stock Sentiment Dashboard", layout="wide")

st.title("📈 Stock Sentiment Dashboard")
st.markdown("View sentiment-labeled news stories for your favorite stocks.")

# Sidebar filters
tickers = list(data.keys())
selected_ticker = st.sidebar.selectbox("📊 Select a Stock", tickers)
sentiment_filter = st.sidebar.multiselect("🧠 Filter by Sentiment", ["positive", "neutral", "negative"], default=["positive", "neutral", "negative"])

st.markdown(f"### 📰 News for `{selected_ticker}`")

# Display articles
for url, article in data[selected_ticker].items():
    if article["sentiment"] not in sentiment_filter:
        continue

    with st.expander(f"🔗 [{article['sentiment'].capitalize()} | {round(article['score']*100)}%] {url}"):
        st.markdown(f"**URL:** [{url}]({url})")
        st.markdown(f"**Sentiment:** `{article['sentiment']}`  \n**Score:** `{article['score']}`")
        st.markdown("**Preview:**")
        st.write(article["text"][:1000] + "..." if len(article["text"]) > 1000 else article["text"])