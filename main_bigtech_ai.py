# -*- coding: utf-8 -*-

import feedparser
import requests
import os
import re
import hashlib
from deep_translator import GoogleTranslator

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK2"]

# 🔥 RSS 소스들
RSS_SOURCES = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "https://openai.com/blog/rss.xml",
    "https://blogs.microsoft.com/feed/",
    "https://blog.google/rss/"
]

# 🎯 BigTech 기업
COMPANIES = {
    "microsoft": "MSFT",
    "google": "GOOG",
    "meta": "META",
    "amazon": "AMZN",
    "apple": "AAPL",
    "openai": "OPENAI"
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


# 🔹 제목 정규화 (중복 제거용)
def normalize_title(title):
    return re.sub(r'[^a-z0-9]', '', title.lower())


# 🔹 기사 점수 계산
def score_article(title, summary):
    title_l = title.lower()
    summary_l = summary.lower()
    text = title_l + " " + summary_l

    score = 0
    company_tag = None

    # 기업 점수
    for name, tag in COMPANIES.items():
        if re.search(r"\b" + name + r"\b", title_l):
            score += 3
            company_tag = tag
        elif re.search(r"\b" + name + r"\b", summary_l):
            score += 2
            company_tag = tag

    # 기술 키워드 점수
    for word in TECH_KEYWORDS:
        if word in text:
            score += 1

    # 제외 키워드 감점
    for word in EXCLUDE_KEYWORDS:
        if word in text:
            score -= 5

    return score, company_tag


# 🔹 디스코드 전송
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

    requests.post(WEBHOOK_URL, json=data)


def send_no_news():
    requests.post(WEBHOOK_URL, json={
        "content": "📭 오늘은 BigTech AI 관련 주요 기술 뉴스가 없습니다."
    })


# 🔥 1️⃣ 모든 RSS 수집
all_articles = []

for url in RSS_SOURCES:
    feed = feedparser.parse(url)
    for entry in feed.entries:
        all_articles.append({
            "title": entry.title,
            "summary": entry.get("summary", ""),
            "link": entry.link
        })


# 🔥 2️⃣ 중복 제거
unique_articles = {}
for article in all_articles:
    key = normalize_title(article["title"])
    if key not in unique_articles:
        unique_articles[key] = article

articles = list(unique_articles.values())


# 🔥 3️⃣ 점수 계산 및 필터링
scored_articles = []

for article in articles:
    score, tag = score_article(article["title"], article["summary"])
    if score >= 5 and tag:  # 기준점
        scored_articles.append({
            "title": f"[{tag}] {article['title']}",
            "summary": article["summary"],
            "link": article["link"],
            "score": score
        })


# 🔥 4️⃣ 점수순 정렬
scored_articles.sort(key=lambda x: x["score"], reverse=True)


# 🔥 5️⃣ 상위 5개 전송
count = 0

for article in scored_articles[:5]:
    clean_summary = re.sub('<.*?>', '', article["summary"])
    translated = GoogleTranslator(source='auto', target='ko').translate(clean_summary[:800])
    send_embed(article["title"], translated, article["link"])
    count += 1


# 🔥 기사 없으면 알림
if count == 0:
    send_no_news()
