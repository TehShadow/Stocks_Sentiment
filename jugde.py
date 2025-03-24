import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# Load FinBERT model
model_name = "ProsusAI/finbert"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# Load news.json with title, timestamp, text
with open("news.json", "r", encoding="utf-8") as f:
    news_data = json.load(f)

news_labeled = {}

for company, articles in news_data.items():
    news_labeled[company] = {}

    for url, article in articles.items():
        text = article.get("text", "").strip()
        title = article.get("title", "Untitled")
        timestamp = article.get("timestamp", "Unknown")

        if not text:
            print(f"⚠️ Skipping empty text for {company}: {url}")
            continue

        try:
            result = sentiment_pipeline(text[:1000])[0]  # Use first 1000 chars
            sentiment = result["label"].lower()
            score = round(result["score"], 3)
        except Exception as e:
            print(f"❌ Error on {url}: {e}")
            sentiment = "unknown"
            score = 0.0

        news_labeled[company][url] = {
            "title": title,
            "timestamp": timestamp,
            "text": text,
            "sentiment": sentiment,
            "score": score
        }

        print(f"{company} | {sentiment} ({score}) ← {title}")

# Save to news_labeled.json
with open("news_labeled.json", "w", encoding="utf-8") as f:
    json.dump(news_labeled, f, ensure_ascii=False, indent=2)

print("\n✅ Saved labeled results to news_labeled.json")