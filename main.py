# -*- coding: utf-8 -*-

import feedparser
import requests
import os
from deep_translator import GoogleTranslator
import re

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]

# Google News AI RSS (영문 기준)
rss_url = "https://news.google.com/rss/search?q=artificial+intelligence"
feed = feedparser.parse(rss_url)

articles = feed.entries


# ❌ 제외할 금융/주식 키워드
exclude_keywords = [
    "stock", "stocks", "share price", "investment",
    "investor", "market", "nasdaq", "earnings",
    "revenue", "ipo", "trading", "funding",
    "valuation", "profit", "crypto"
]

# ✅ 포함할 AI 기술 키워드
include_keywords = [
    "model", "research", "openai", "deepmind",
    "anthropic", "llm", "machine learning",
    "neural", "foundation model", "ai chip",
    "semiconductor", "training", "inference",
    "generative", "large language model",
    "gpu", "robotics", "vision model"
]


def is_real_ai_tech_article(title, summary):
    text = (title + " " + summary).lower()

    # 금융 기사 제외
    for word in exclude_keywords:
        if word in text:
            return False

    # AI 기술 키워드 하나라도 포함되어야 통과
    for word in include_keywords:
        if word in text:
            return True

    return False


def send_to_discord(title, summary, link):
    data = {
        "embeds": [
            {
                "title": title,
                "url": link,
                "description": summary,
                "color": 5814783
            }
        ]
    }

    requests.post(WEBHOOK_URL, json=data)


# 필터링 후 상위 5개 전송
count = 0

for article in articles:
    if count >= 5:
        break

    if not is_real_ai_tech_article(article.title, article.summary):
        continue

    clean_summary = re.sub('<.*?>', '', article.summary)
    translated = GoogleTranslator(source='auto', target='ko').translate(clean_summary[:800])

    send_to_discord(article.title, translated, article.link)

    count += 1
