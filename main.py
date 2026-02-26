import feedparser
import requests
import os
from datetime import datetime
from deep_translator import GoogleTranslator

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]

# RSS 뉴스 가져오기 (TechCrunch 예시)
rss_url = "https://news.google.com/rss/search?q=artificial+intelligence"
feed = feedparser.parse(rss_url)

articles = feed.entries[:5]

for article in articles:
    message = analyze_article(article.title, article.summary)
    send_to_discord(message)

def analyze_article(title, summary):
    # HTML 태그 제거 (구글뉴스용)
    import re
    clean_summary = re.sub('<.*?>', '', summary)

    # 영어 → 한국어 번역
    translated = GoogleTranslator(source='auto', target='ko').translate(clean_summary[:800])

    return f"""
📌 **{title}**

📰 한글 요약:
{translated}

🔎 왜 중요한가:
AI 산업의 최신 동향을 보여주는 사례임.

📈 향후 영향:
관련 산업 및 기술 발전에 영향 가능성.
"""

def send_to_discord(message):
    data = {
        "content": message
    }
    requests.post(WEBHOOK_URL, json=data)

for article in articles:
    message = analyze_article(article.title, article.summary)
    send_to_discord(message)
