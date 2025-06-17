import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_polling
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from googletrans import Translator
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
LANGUAGE_CHANNELS = {
    "ru": -1001111111111,
    "ua": -1002222222222,
    "en": -1003333333333,
    "pl": -1004444444444
}
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

translator = Translator()

class PostStates(StatesGroup):
    waiting_for_post_text = State()

async def send_post_to_channels(text: str):
    translations = {}
    for lang in LANGUAGE_CHANNELS.keys():
        if lang == "ru":
            translations[lang] = text
        else:
            try:
                translated = translator.translate(text, src="ru", dest=lang)
                translations[lang] = translated.text
            except Exception as e:
                logging.error(f"Error translating to {lang}: {e}")
                translations[lang] = text

    for lang, channel_id in LANGUAGE_CHANNELS.items():
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
    await PostStates.waiting_for_post_text.set()

@dp.message_handler(state=PostStates.waiting_for_post_text, content_types=types.ContentTypes.TEXT)
async def handle_post_text(message: types.Message, state: FSMContext):
    text = message.text
    await send_post_to_channels(text)
    await message.answer("Пост отправлен в каналы.")
    await state.finish()

async def periodic_api_check():
    while True:
        # Тут можно запросить API и отправить новые посты, если нужно
        await asyncio.sleep(3600)

async def on_startup(_):
    logging.info("Бот запущен")
    asyncio.create_task(periodic_api_check())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_polling(dp, on_startup=on_startup)
