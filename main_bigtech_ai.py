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

# ❌ 금융/정치 제거 키워드
exclude_keywords = [
    "stock", "stocks", "share price", "investment",
    "investor", "market", "nasdaq", "earnings",
    "revenue", "ipo", "trading", "funding",
    "valuation", "profit",
    "bill", "senate", "congress", "law",
    "government", "regulation", "political"
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
    text = (title + " " + summary).lower()

    # ① 제목에 기업명이 정확히 포함되어야 함
    company_found = False
    for company in target_companies:
        pattern = r"\b" + company + r"\b"
        if re.search(pattern, title_lower):
            company_found = True
            break

    if not company_found:
        return False

    # ② 기술 키워드 필수
    if not any(word in text for word in tech_keywords):
        return False

    # ③ 금융/정치 키워드 있으면 제외
    if any(word in text for word in exclude_keywords):
        return False

    return True


def send_to_discord(title, summary, link):
    data = {
        "embeds": [
            {
                "title": title,
                "url": link,
                "description": summary,
                "color": 3447003
            }
        ]
    }

    requests.post(WEBHOOK_URL, json=data)


# 🔥 기사 5개 전송
count = 0

for article in articles:
    if count >= 5:
        break

    if not is_valid_article(article.title, article.summary):
        continue

    clean_summary = re.sub('<.*?>', '', article.summary)
    translated = GoogleTranslator(source='auto', target='ko').translate(clean_summary[:800])

    send_to_discord(article.title, translated, article.link)

    count += 1
