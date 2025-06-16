from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
import os
import feedparser
from google.cloud import translate_v2 as translate
from google.cloud import vision
import requests

bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
dp = Dispatcher()
translator = translate.Client()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🍏 Отправь фото еды для анализа калорий или напиши /workout для плана тренировок.")

@dp.message(lambda msg: msg.photo)
async def analyze_photo(message: types.Message):
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    img_url = f"https://api.telegram.org/file/bot{os.getenv('TELEGRAM_TOKEN')}/{file.file_path}"

    vision_client = vision.ImageAnnotatorClient()
    image = vision.Image(source=vision.ImageSource(image_uri=img_url))
    response = vision_client.label_detection(image=image)

    labels = [label.description for label in response.label_annotations]
    food_item = labels[0] if labels else "еда"

    nutritionix_url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {"x-app-id": os.getenv("NUTRITIONIX_ID"), "x-app-key": os.getenv("NUTRITIONIX_KEY")}
    data = {"query": f"100g {food_item}"}

    try:
        calories = requests.post(nutritionix_url, headers=headers, json=data).json()["foods"][0]["nf_calories"]
        await message.answer(f"🍽 {food_item}: ~{calories} ккал на 100г")
    except:
        await message.answer("⚠ Не удалось определить калории. Попробуйте другое фото.")

@dp.message(Command("workout"))
async def generate_workout(message: types.Message):
    text = '''
    💪 Ваш план тренировок (вес 75 кг, рост 168 см):
    - Пн: Кардио 30 мин + пресс.
    - Ср: Силовая (приседания, отжимания).
    - Пт: Плавание или велосипед.
    '''
    await message.answer(text)
