import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_polling
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from googletrans import Translator
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")

CHANNELS = {
    "ru": int(os.getenv("CHANNEL_RU")),
    "ua": int(os.getenv("CHANNEL_UA")),
    "en": int(os.getenv("CHANNEL_EN")),
    "pl": int(os.getenv("CHANNEL_PL")),
}

ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

translator = Translator()

async def send_post_to_channels(text: str):
    translations = {}
    for lang in CHANNELS.keys():
        if lang == "ru":
            translations[lang] = text
        else:
            try:
                translated = translator.translate(text, src="ru", dest=lang)
                translations[lang] = translated.text
            except Exception as e:
                logging.error(f"Error translating to {lang}: {e}")
                translations[lang] = text

    for lang, channel_id in CHANNELS.items():
        try:
            await bot.send_message(channel_id, translations[lang])
        except Exception as e:
            logging.error(f"Error sending message to {lang} channel: {e}")

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Привет, Админ! Отправь мне текст поста, и я переведу и разошлю его.")
    else:
        await message.answer("Привет! Этот бот публикует посты в каналы.")

@dp.message_handler(commands=["post"])
async def cmd_post(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет прав отправлять посты.")
        return
    await message.answer("Отправьте текст поста для рассылки:")

    @dp.message_handler(lambda m: m.from_user.id == ADMIN_ID)
    async def handle_post_text(post_message: types.Message):
        text = post_message.text
        await send_post_to_channels(text)
        await post_message.answer("Пост отправлен в каналы.")
        dp.message_handlers.unregister(handle_post_text)

async def periodic_api_check():
    while True:
        # Тут можно запросить API и отправить новые посты
        await asyncio.sleep(3600)

async def on_startup(_):
    logging.info("Бот запущен")
    asyncio.create_task(periodic_api_check())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_polling(dp, on_startup=on_startup)
