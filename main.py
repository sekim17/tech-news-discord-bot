# -*- coding: utf-8 -*-

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

    message = "**" + title + "**\n\n"
    message += translated + "\n\n"
    message += "원문: " + link

    return message


def send_to_discord(message):
    data = {
        "content": message
    }
    requests.post(WEBHOOK_URL, json=data)


# 실행 부분 (맨 아래)
for article in articles:
    message = analyze_article(article.title, article.summary, article.link)
    send_to_discord(message)
