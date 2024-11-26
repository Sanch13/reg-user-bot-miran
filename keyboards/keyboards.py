from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import settings


def get_inline_keyboard_full_name() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="Ввести данные",
                                 callback_data="first_name"),
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_button_reg() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="Регистрация",
                                 url=settings.CHANNEL_LINK_MIRAN),
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
