from aiogram import Dispatcher, Bot, Router

from config import settings

bot = Bot(token=settings.API_TELEGRAM_TOKEN.get_secret_value())
dp = Dispatcher()
router = Router()
dp.include_router(router)
