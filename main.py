import feedparser
import requests
import os
from deep_translator import GoogleTranslator
import re

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]

# RSS 뉴스 가져오기
rss_url = "https://news.google.com/rss/search?q=artificial+intelligence"
feed = feedparser.parse(rss_url)

articles = feed.entries[:5]


def analyze_article(title, summary):
    # HTML 태그 제거
    clean_summary = re.sub('<.*?>', '', summary)

    # 영어 → 한국어 번역
    translated = GoogleTranslator(source='auto', target='ko').translate(clean_summary[:800])

    return f"""
📌 **{title}**

📰 한글 요약:
{translated}
"""

def send_to_discord(message):
    data = {
        "content": message
    }
    requests.post(WEBHOOK_URL, json=data)


# 👇 반드시 맨 아래에서 실행
for article in articles:
    message = analyze_article(article.title, article.summary)
    send_to_discord(message)
