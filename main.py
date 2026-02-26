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


def analyze_article(title, summary, link):
    clean_summary = re.sub('<.*?>', '', summary)
    translated = GoogleTranslator(source='auto', target='ko').translate(clean_summary[:800])

    return f"**{title}**\n\n{translated}\n\n원문: {link}"

📰 한글 요약:
{translated}

🔗 원문 보기:
{link}
"""

def send_to_discord(message):
    data = {
        "content": message
    }
    requests.post(WEBHOOK_URL, json=data)


# 👇 반드시 맨 아래에서 실행
for article in articles:
    message = analyze_article(article.title, article.summary, article.link)
    send_to_discord(message)
