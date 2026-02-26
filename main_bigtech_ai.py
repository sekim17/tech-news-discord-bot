# -*- coding: utf-8 -*-

import feedparser
import requests
import os
import re
from deep_translator import GoogleTranslator

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK2"]

# 🔥 RSS 소스
RSS_SOURCES = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "https://openai.com/blog/rss.xml",
    "https://blogs.microsoft.com/feed/",
    "https://blog.google/rss/"
]

# 🎯 기업 태그 + 색상
COMPANIES = {
    "microsoft": {"tag": "MSFT", "color": 0x0078D4},
    "google": {"tag": "GOOG", "color": 0x4285F4},
    "meta": {"tag": "META", "color": 0x0668E1},
    "amazon": {"tag": "AMZN", "color": 0xFF9900},
    "apple": {"tag": "AAPL", "color": 0x111111},
    "openai": {"tag": "OPENAI", "color": 0x10A37F}
}

TECH_KEYWORDS = [
    "ai", "model", "llm", "machine learning",
    "neural", "training", "inference",
    "chip", "gpu", "semiconductor",
    "generative", "robotics",
    "foundation model"
]

EXCLUDE_KEYWORDS = [
    "stock", "market", "earnings",
    "revenue", "investment", "ipo",
    "senate", "law", "government",
    "election", "political"
]


def normalize_title(title):
    return re.sub(r'[^a-z0-9]', '', title.lower())


def score_article(title, summary):
    title_l = title.lower()
    summary_l = summary.lower()
    text = title_l + " " + summary_l

    score = 0
    company_data = None

    for name, data in COMPANIES.items():
        if re.search(r"\b" + name + r"\b", title_l):
            score += 3
            company_data = data
        elif re.search(r"\b" + name + r"\b", summary_l):
            score += 2
            company_data = data

    for word in TECH_KEYWORDS:
        if word in text:
            score += 1

    for word in EXCLUDE_KEYWORDS:
        if word in text:
            score -= 5

    return score, company_data


def send_embed(title, description, link, color):
    data = {
        "embeds": [
            {
                "title": title,
                "url": link,
                "description": description,
                "color": color
            }
        ]
    }

    requests.post(WEBHOOK_URL, json=data)


def send_no_news():
    requests.post(WEBHOOK_URL, json={
        "content": "📭 오늘은 BigTech AI 관련 주요 기술 뉴스가 없습니다."
    })


# 🔥 RSS 수집
all_articles = []

for url in RSS_SOURCES:
    feed = feedparser.parse(url)
    for entry in feed.entries:
        all_articles.append({
            "title": entry.title,
            "summary": entry.get("summary", ""),
            "link": entry.link
        })


# 🔥 중복 제거
unique_articles = {}
for article in all_articles:
    key = normalize_title(article["title"])
    if key not in unique_articles:
        unique_articles[key] = article

articles = list(unique_articles.values())


# 🔥 점수 계산
scored_articles = []

for article in articles:
    score, company_data = score_article(article["title"], article["summary"])
    if score >= 5 and company_data:
        scored_articles.append({
            "title": f"[{company_data['tag']}] {article['title']}",
            "summary": article["summary"],
            "link": article["link"],
            "score": score,
            "color": company_data["color"]
        })


# 🔥 점수순 정렬
scored_articles.sort(key=lambda x: x["score"], reverse=True)


# 🔥 상위 5개 전송
count = 0

for article in scored_articles[:5]:
    clean_summary = re.sub('<.*?>', '', article["summary"])
    translated = GoogleTranslator(source='auto', target='ko').translate(clean_summary[:800])

    send_embed(
        article["title"],
        translated,
        article["link"],
        article["color"]
    )

    count += 1


if count == 0:
    send_no_news()
