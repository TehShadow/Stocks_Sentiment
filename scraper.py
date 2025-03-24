import json
import re
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# List of stock tickers
stock_symbols = ["TSLA", "NVDA"]

# Dictionary to store results
all_news = {}

# Setup headless Firefox
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, 10)

def accept_cookies_once():
    try:
        agree_button = wait.until(EC.presence_of_element_located((By.NAME, "agree")))
        driver.execute_script("arguments[0].click();", agree_button)
        print("✅ Accepted cookies")
    except:
        print("⚠️ Cookie already accepted or not shown")

def get_main_text_from_url(url):
    try:
        driver.get(url)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Try to find the main article content
        article = soup.find("article") or soup.find("div", {"class": re.compile(r"(caas-body|article|content)")})
        if not article:
            return None

        paragraphs = article.find_all(["p", "h2"])
        full_text = "\n".join(p.get_text(strip=True) for p in paragraphs)
        return full_text if full_text else None
    except Exception as e:
        print(f"❌ Failed to extract article: {e}")
        return None

def scrape_news_for_symbol(symbol):
    url = f"https://finance.yahoo.com/quote/{symbol}/"
    driver.get(url)

    if symbol == stock_symbols[0]:
        accept_cookies_once()

    try:
        wait.until(EC.presence_of_element_located((
            By.XPATH, '/html/body/div[2]/main/section/section/section/article/section[3]/div[2]'
        )))
    except Exception as e:
        print(f"❌ News section not found for {symbol}: {e}")
        return

    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    news_div = soup.select_one("section:nth-of-type(3) > div:nth-of-type(2)")

    if not news_div:
        print(f"⚠️ Could not parse news section for {symbol}")
        return

    seen = set()
    articles = news_div.find_all("a")
    all_news[symbol] = {}

    for article in articles:
        title = article.get_text(strip=True)
        href = article.get("href", "")

        if not title:
            continue
        if "ads" in href or "partner" in href or "doubleclick" in href or "taboola" in href:
            continue
        if not href.startswith("http"):
            href = "https://finance.yahoo.com" + href
        if href in seen:
            continue

        seen.add(href)

        story = get_main_text_from_url(href)
        if story:
            all_news[symbol][href] = story
            print(f"✅ {symbol} → {title}")
        else:
            print(f"⚠️ Skipped (no content): {href}")

try:
    for symbol in stock_symbols:
        scrape_news_for_symbol(symbol)
finally:
    driver.quit()

# Save to JSON
with open("news.json", "w", encoding="utf-8") as f:
    json.dump(all_news, f, ensure_ascii=False, indent=2)

print("\n💾 Saved all articles to news.json")
