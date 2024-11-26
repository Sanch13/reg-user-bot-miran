from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from init_bot import router
from keyboards.keyboards import get_inline_keyboard_full_name, get_button_reg
from middleware.middleware import check_subscribe
from validators.validators import validate_string
from utils.utils_for_db import save_user
from utils.utils import send_email


class Registration(StatesGroup):
    first_name = State()
    last_name = State()
    middle_name = State()
    button = State()


@router.message(CommandStart())
@check_subscribe
async def cmd_start(message: Message):
    keyboard = get_inline_keyboard_full_name()
    await message.answer(
        text=f"Приветствую тебя\nДля регистрации в нашем телеграм канале введите свои личные данные",
        reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data == "first_name")
async def process_input_first_name(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(Registration.last_name)
    await callback_query.message.answer("Введите ваше имя:")
    await callback_query.answer()


@router.message(Registration.last_name)
async def process_input_last_name(message: Message,  state: FSMContext):
    if not await validate_string(message):
        await message.answer("Только русские буквы.")
        return

    await state.update_data(first_name=message.text.strip())
    await state.set_state(Registration.middle_name)
    await message.answer("Введите вашу фамилию:")


@router.message(Registration.middle_name)
async def process_input_middle_name(message: Message,  state: FSMContext):
    if not await validate_string(message):
        await message.answer("Только русские буквы.")
        return

    await state.update_data(last_name=message.text.strip())
    await state.set_state(Registration.button)
    await message.answer("Введите ваше отчество:")


@router.message(Registration.button)
async def process_show_button_to_chanel(message: Message, state: FSMContext):
    if not await validate_string(message):
        await message.answer("Только русские буквы.")
        return

    telegram_id = message.from_user.id
    await state.update_data(middle_name=message.text.strip())
    data = await state.get_data()

    first_name, middle_name, last_name = data.values()
    full_name = f"{first_name} {middle_name} {last_name}"
    full_name_from_tg = message.from_user.full_name or ""

    await save_user(
        telegram_id=telegram_id,
        full_name=full_name,
        full_name_from_tg=full_name_from_tg
    )

    await send_email(telegram_id, full_name, full_name_from_tg)

    keyboards = get_button_reg()
    await message.answer(
        f"""Спасибо!\nЧтобы зарегистрироваться нажмите на кнопку Регистрация""",
        reply_markup=keyboards
    )

    await state.clear()
