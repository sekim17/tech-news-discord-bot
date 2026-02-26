import feedparser
import requests
import os
from datetime import datetime

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]

# RSS 뉴스 가져오기 (TechCrunch 예시)
rss_url = "https://news.google.com/rss/search?q=artificial+intelligence"
feed = feedparser.parse(rss_url)

articles = [
    entry for entry in feed.entries
    if "AI" in entry.title or "Artificial" in entry.title
][:5]

def analyze_article(title, summary):
    # 간단 분석 템플릿 (무료 버전)
    return f"""
📌 **{title}**

📰 요약:
{summary[:500]}

🔍 왜 중요한가:
이 기사는 기술 산업의 최신 흐름을 보여주며 시장 및 연구 방향에 영향을 줄 가능성이 있음.

📈 향후 영향:
관련 기술 투자 및 산업 경쟁 심화 예상.
"""

def send_to_discord(message):
    data = {
        "content": message
    }
    requests.post(WEBHOOK_URL, json=data)

for article in articles:
    message = analyze_article(article.title, article.summary)
    send_to_discord(message)
