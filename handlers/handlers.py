from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from init_bot import router
from keyboards.keyboards import get_inline_keyboard_full_name, get_button_reg
from validators.validators import validate_full_name
from utils.utils_for_db import save_user, is_exists_user


class Registration(StatesGroup):
    full_name = State()
    button = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    keyboard = get_inline_keyboard_full_name()
    await message.answer(
        text=f"""Приветствую тебя\nДля регистрации в нашем телеграм канале введите ФИО""",
        reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data == "full_name")
async def process_input_full_name(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(Registration.button)
    await callback_query.message.answer("Введите ваше ФИО:")
    await callback_query.answer()


@router.message(Registration.button)
async def process_name_parent(message: Message, state: FSMContext):
    telegram_id = message.from_user.id

    try:
        validate_full_name(message.text)
        full_name = message.text.strip()
    except Exception as error:
        await message.answer(
            "ФИО должно содержать только русские или английские буквы.\nВведите ваше ФИО:"
        )
        return

    await state.update_data(full_name=full_name)
    data = await state.get_data()

    if await is_exists_user(telegram_id=telegram_id):
        await message.answer(f"""Упс!\nВы уже зарегистрированы.""")
    else:
        full_name = data.get("full_name", '')
        full_name_from_tg = message.from_user.full_name

        await save_user(
            telegram_id=telegram_id,
            full_name=full_name,
            full_name_from_tg=full_name_from_tg
        )

        keyboards = get_button_reg()
        await message.answer(
            f"""Спасибо!\nЧтобы зарегистрироваться нажмите на кнопку Регистрация""",
            reply_markup=keyboards
        )

    await state.clear()

