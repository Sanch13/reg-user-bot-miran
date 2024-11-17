from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_inline_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="Регистрация",
                                 callback_data="registration"),
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_inline_keyboard_yes_no() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="Да", callback_data="yes"),
            InlineKeyboardButton(text="Нет", callback_data="no"),
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
