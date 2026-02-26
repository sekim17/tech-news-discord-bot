# -*- coding: utf-8 -*-

import feedparser
import requests
import os
from deep_translator import GoogleTranslator
import re

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK2"]

rss_url = "https://news.google.com/rss/search?q=artificial+intelligence"
feed = feedparser.parse(rss_url)

articles = feed.entries


# 🎯 6개 기업
target_companies = [
    "microsoft",
    "google",
    "meta",
    "amazon",
    "apple",
    "openai"
]

# ❌ 금융/정치 제외 키워드
exclude_keywords = [
    "stock", "stocks", "share price", "investment",
    "investor", "market", "nasdaq", "earnings",
    "revenue", "ipo", "trading", "funding",
    "valuation", "profit",
    "bill", "senate", "congress", "law",
    "government", "regulation", "political",
    "election"
]

# ✅ 기술 키워드
tech_keywords = [
    "model", "llm", "machine learning",
    "neural", "training", "inference",
    "chip", "gpu", "semiconductor",
    "generative", "robotics", "vision",
    "foundation model", "research",
    "artificial intelligence", "ai system"
]


def is_valid_article(title, summary):
    title_lower = title.lower()
    summary_lower = summary.lower()
    text = title_lower + " " + summary_lower

    # ① 기업명이 title 또는 summary에 있어야 함
    company_found = False
    for company in target_companies:
        pattern = r"\b" + company + r"\b"
        if re.search(pattern, title_lower) or re.search(pattern, summary_lower):
            company_found = True
            break

    if not company_found:
        return False

    # ② 기술 키워드 필수
    if not any(word in text for word in tech_keywords):
        return False

    # ③ 금융/정치 기사 제외
    if any(word in text for word in exclude_keywords):
        return False

    return True


def send_embed(title, description, link):
    data = {
        "embeds": [
            {
                "title": title,
                "url": link,
                "description": description,
                "color": 3447003
            }
        ]
    }

    response = requests.post(WEBHOOK_URL, json=data)
    print("Discord status:", response.status_code)


def send_no_news_message():
    data = {
        "content": "📭 오늘은 BigTech AI 관련 주요 기술 뉴스가 없습니다."
    }

    response = requests.post(WEBHOOK_URL, json=data)
    print("No news message status:", response.status_code)


# 🔥 실행 로직
count = 0

for article in articles:
    if count >= 5:
        break

    if not is_valid_article(article.title, article.summary):
        continue

    clean_summary = re.sub('<.*?>', '', article.summary)
    translated = GoogleTranslator(source='auto', target='ko').translate(clean_summary[:800])

    send_embed(article.title, translated, article.link)

    count += 1


# 📭 기사 없으면 자동 메시지 전송
if count == 0:
    send_no_news_message()

print("Total sent:", count)
