from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import settings
from init_bot import bot
from keyboards import get_inline_keyboard
from utils_for_db import is_user_registration


def check_subscribe(func):
    """Checking user subscribing on the group or channel"""
    async def wrapper(message: Message, state: FSMContext):
        user_id = message.from_user.id
        status = await bot.get_chat_member(chat_id=settings.CHANNEL_ID_MIRAN, user_id=user_id)
        if status.status in ('member', 'creator', 'administrator'):
            await func(message, state)
        else:
            text = f"\nВы не подписаны на наш телеграм-канал  {settings.CHANNEL_LINK}." \
                   f"\nПожалуйста, подпишитесь"
            await message.answer('')
            await bot.send_message(user_id, text=text, reply_markup=get_inline_keyboard())
    return wrapper


def check_registration(func):
    """Checking user registrations"""
    async def wrapper(message: Message, state: FSMContext):
        user_id = message.from_user.id
        if await is_user_registration(user_id=user_id):
            text = f"Вы уже зарегистрировались"
            await message.answer('')
            await bot.send_message(user_id, text=text)
        else:
            await func(message, state)
    return wrapper
