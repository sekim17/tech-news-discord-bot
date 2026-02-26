# -*- coding: utf-8 -*-

import feedparser
import requests
import os
from deep_translator import GoogleTranslator
import re

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]

rss_url = "https://news.google.com/rss/search?q=artificial+intelligence"
feed = feedparser.parse(rss_url)

articles = feed.entries


target_companies = [
    "microsoft",
    "google",
    "meta",
    "amazon",
    "apple",
    "openai"
]

exclude_keywords = [
    "stock", "stocks", "share price", "investment",
    "investor", "market", "nasdaq", "earnings",
    "revenue", "ipo", "trading", "funding",
    "valuation", "profit"
]

tech_keywords = [
    "model", "ai model", "llm", "machine learning",
    "neural", "training", "inference",
    "chip", "gpu", "semiconductor",
    "generative", "robotics", "vision model",
    "foundation model", "research"
]


def is_bigtech_ai_article(title, summary):
    text = (title + " " + summary).lower()

    if not any(company in text for company in target_companies):
        return False

    if any(word in text for word in exclude_keywords):
        return False

    if not any(word in text for word in tech_keywords):
        return False

    return True


def send_to_discord(title, summary, link):
    data = {
        "embeds": [
            {
                "title": title,
                "url": link,
                "description": summary,
                "color": 15105570  # 보라색 계열 (구분용)
            }
        ]
    }

    requests.post(WEBHOOK_URL, json=data)


count = 0

for article in articles:
    if count >= 5:
        break

    if not is_bigtech_ai_article(article.title, article.summary):
        continue

    clean_summary = re.sub('<.*?>', '', article.summary)
    translated = GoogleTranslator(source='auto', target='ko').translate(clean_summary[:800])

    send_to_discord(article.title, translated, article.link)

    count += 1
