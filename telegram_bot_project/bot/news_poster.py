import feedparser
from aiogram import Bot
import os

bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))

async def post_news():
    news = feedparser.parse("https://rss.health.com/nutrition")
    for entry in news.entries[:3]:
        await bot.send_message(chat_id="@your_channel", text=entry.title)
