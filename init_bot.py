import os

from dotenv import load_dotenv

from aiogram import Dispatcher, Bot, Router

# from config import settings

load_dotenv()

bot = Bot(token=os.getenv("API_TELEGRAM_TOKEN"))
dp = Dispatcher()
router = Router()
dp.include_router(router)
