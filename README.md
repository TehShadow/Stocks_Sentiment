# 📈 Stock Sentiment Dashboard

A fully offline web app for scraping, analyzing, and displaying stock-related news sentiment using FinBERT and Yahoo Finance.

---

## 🚀 Features
- ✅ User inputs a stock ticker (e.g., `AAPL`, `TSLA`, `NVDA`)
- ✅ Scrapes latest news headlines and articles from Yahoo Finance
- ✅ Extracts title, timestamp, and full article text
- ✅ Runs offline sentiment analysis using `ProsusAI/finbert`
- ✅ Displays results in an interactive Streamlit dashboard
- ✅ Filter by sentiment type (positive, neutral, negative)
- ✅ Clickable titles with article previews

---

## 🧰 Requirements
```bash
pip install streamlit selenium transformers torch beautifulsoup4
```

You also need:
- `geckodriver` for Firefox (in your PATH)
- Firefox installed

---


---

## ▶️ Run the App
```bash
streamlit run stock_sentiment_app.py
```

---

## 🧠 Behind the Scenes
- Scraper loads news using `selenium` + `BeautifulSoup`
- Analyzer uses `ProsusAI/finbert` from Hugging Face for local sentiment classification
- Dashboard updates on-the-fly with scraping and analysis


