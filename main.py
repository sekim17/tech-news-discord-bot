# -*- coding: utf-8 -*-

import feedparser
import requests
import os
from deep_translator import GoogleTranslator
import re

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]

# Google News AI RSS
rss_url = "https://news.google.com/rss/search?q=artificial+intelligence"
feed = feedparser.parse(rss_url)

articles = feed.entries[:5]


def send_to_discord(title, summary, link):
    data = {
        "embeds": [
            {
                "title": title,      # 제목 (클릭 가능)
                "url": link,         # 제목 클릭 시 이동
                "description": summary,
                "color": 5814783     # 파란 계열 색상
            }
        ]
    }

    requests.post(WEBHOOK_URL, json=data)


# 실행 부분
for article in articles:
    clean_summary = re.sub('<.*?>', '', article.summary)
    translated = GoogleTranslator(source='auto', target='ko').translate(clean_summary[:800])

    send_to_discord(article.title, translated, article.link)
