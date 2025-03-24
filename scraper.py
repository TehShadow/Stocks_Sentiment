import os
import json
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ===== USER INPUT =====
symbol = input("Enter stock ticker (e.g. TSLA, AAPL): ").strip().upper()

# ===== SETUP =====
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, 10)

# ===== FINBERT SETUP =====
model_name = "ProsusAI/finbert"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

news_data = {}
news_labeled = {}

# ===== ACCEPT COOKIES =====
def accept_cookies():
    try:
        agree_button = wait.until(EC.presence_of_element_located((By.NAME, "agree")))
        driver.execute_script("arguments[0].click();", agree_button)
        print("✅ Accepted cookies")
    except:
        pass

# ===== EXTRACT FULL ARTICLE =====
def get_article_details(url):
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        title = soup.find("cover-title") or soup.find("title")
        title_text = title.get_text(strip=True) if title else "No Title"

        time_tag = soup.find("time")
        if time_tag and time_tag.has_attr("datetime"):
            timestamp = time_tag["datetime"]
        elif time_tag:
            timestamp = time_tag.get_text(strip=True)
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        article = soup.find("article") or soup.find("div", {"class": re.compile(r"(caas-body|article|content)")})
        if not article:
            return None

        paragraphs = article.find_all(["p", "h2"])
        full_text = "\n".join(p.get_text(strip=True) for p in paragraphs)

        return {
            "title": title_text,
            "timestamp": timestamp,
            "text": full_text if full_text else "No content"
        }

    except Exception as e:
        print(f"❌ Error scraping article: {url} → {e}")
        return None

# ===== SCRAPE NEWS HEADLINES =====
def scrape_news_for_symbol(symbol):
    url = f"https://finance.yahoo.com/quote/{symbol}/"
    driver.get(url)
    accept_cookies()

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/main/section/section/section/article/section[3]/div[2]')))
    except:
        print(f"❌ Could not find news section for {symbol}")
        return {}

    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    news_div = soup.select_one("section:nth-of-type(3) > div:nth-of-type(2)")
    if not news_div:
        return {}

    seen = set()
    articles = {}

    for a in news_div.find_all("a"):
        title = a.get_text(strip=True)
        href = a.get("href", "")

        if not title or "ads" in href or "partner" in href or "doubleclick" in href or "taboola" in href or "plans/select-plan" in href or "premiumNews" in href:
            continue
        if not href.startswith("http"):
            href = "https://finance.yahoo.com" + href
        if href in seen:
            continue

        seen.add(href)
        story = get_article_details(href)
        if story:
            articles[href] = {
                "title": story["title"],
                "timestamp": story["timestamp"],
                "text": story["text"]
            }
            print(f"✅ Scraped: {story['title']}")

    return articles

# ===== ANALYZE SENTIMENT =====
def label_sentiment(data):
    labeled = {}
    for url, article in data.items():
        text = article.get("text", "").strip()
        if not text:
            continue

        try:
            result = sentiment_pipeline(text[:1000])[0]
            sentiment = result["label"].lower()
            score = round(result["score"], 3)
        except Exception as e:
            print(f"⚠️ Error analyzing {url}: {e}")
            sentiment = "unknown"
            score = 0.0

        labeled[url] = {
            "title": article["title"],
            "timestamp": article["timestamp"],
            "text": text,
            "sentiment": sentiment,
            "score": score
        }
        print(f"🔍 {sentiment} ({score}) → {article['title']}")

    return labeled

# ===== MAIN PIPELINE =====
try:
    articles = scrape_news_for_symbol(symbol)
    news_data[symbol] = articles
    labeled = label_sentiment(articles)
    news_labeled[symbol] = labeled
finally:
    driver.quit()

# Save outputs
with open("news.json", "w", encoding="utf-8") as f:
    json.dump(news_data, f, ensure_ascii=False, indent=2)

with open("news_labeled.json", "w", encoding="utf-8") as f:
    json.dump(news_labeled, f, ensure_ascii=False, indent=2)

print("\n✅ Done. Saved news and labeled sentiment.")
