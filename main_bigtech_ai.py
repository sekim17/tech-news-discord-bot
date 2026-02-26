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


# 🎯 정확히 이 6개 기업만
target_companies = [
    "microsoft",
    "google",
    "meta",
    "amazon",
    "apple",
    "openai"
]

# ❌ 금융/주식 제거
exclude_keywords = [
    "stock", "stocks", "share price", "investment",
    "investor", "market", "nasdaq", "earnings",
    "revenue", "ipo", "trading", "funding",
    "valuation", "profit"
]

# ✅ 기술 키워드 (하나 이상 포함 필수)
tech_keywords = [
    "model", "llm", "machine learning",
    "neural", "training", "inference",
    "chip", "gpu", "semiconductor",
    "generative", "robotics", "vision",
    "foundation model", "research",
    "artificial intelligence", "ai system"
]


def contains_company_as_main_subject(title, summary):
    """
    1️⃣ 제목에 회사명이 정확한 단어로 포함되면 강하게 통과
    2️⃣ 요약에만 등장하면 약하게 허용 (기술 키워드와 함께 있을 때만)
    """
    title_lower = title.lower()
    summary_lower = summary.lower()

    for company in target_companies:
        pattern = r"\b" + company + r"\b"

        # 제목에 등장 → 거의 주체일 확률 높음
        if re.search(pattern, title_lower):
            return True

        # 요약에 등장 + 기술 키워드 같이 존재할 때만 허용
        if re.search(pattern, summary_lower):
            if any(word in summary_lower for word in tech_keywords):
                return True

    return False


def is_valid_ai_bigtech_article(title, summary):
    tl = title.lower()

    # ① 제목에 정확히 기업명이 있어야 함
    if not any(re.search(r"\b" + c + r"\b", tl) for c in target_companies):
        return False

    text = (title + " " + summary).lower()

    # ② 기술 키워드도 (title 또는 summary) 있어야 함
    if not any(word in text for word in tech_keywords):
        return False

    # ③ 금융/정치/주식 키워드 있으면 제외
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
                "color": 15105570
            }
        ]
    }

    requests.post(WEBHOOK_URL, json=data)


# 🔥 필터 후 5개 전송
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
