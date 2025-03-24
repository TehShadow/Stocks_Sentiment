import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from pathlib import Path

# Load the FinBERT model
model_name = "ProsusAI/finbert"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# Load news.json
with open("news.json", "r", encoding="utf-8") as f:
    news_data = json.load(f)

news_labeled = {}

# Loop through all articles
for company, articles in news_data.items():
    news_labeled[company] = {}
    for url, text in articles.items():
        short_text = text[:1000]  # Truncate for performance and length limit
        try:
            result = sentiment_pipeline(short_text)[0]
            sentiment = result["label"].lower()
            score = round(result["score"], 3)
        except Exception as e:
            print(f"⚠️ Error analyzing {url}: {e}")
            sentiment = "unknown"
            score = 0

        news_labeled[company][url] = {
            "sentiment": sentiment,
            "score": score,
            "text": text
        }

        print(f"{company} | {sentiment} ({score}) ← {url}")

# Save the labeled output
with open("news_labeled.json", "w", encoding="utf-8") as f:
    json.dump(news_labeled, f, ensure_ascii=False, indent=2)

print("\n✅ Saved labeled results to news_labeled.json")
