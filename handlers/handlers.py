import asyncio
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from init_bot import router
from keyboards.keyboards import (
    get_inline_keyboard_enter_data,
    get_button_reg,
    get_inline_keyboard_yes_no
)
from middleware.middleware import check_subscribe
from validators.validators import validate_string
from utils.utils_for_db import save_user, get_user_by_id, update_is_active_user_by_id
from utils.utils import (
    send_email,
    get_data_user,
    check_user_in_group_and_notify,
    normalize_full_name
)
from logs.logging_config import logger


class Registration(StatesGroup):
    waiting_for_consent = State()
    last_name = State()
    first_name = State()
    middle_name = State()


@router.message(CommandStart())
@check_subscribe
async def cmd_start(message: Message):
    keyboard = get_inline_keyboard_enter_data()
    await message.answer(
        text=f'Для регистрации введите ваши ФИО\nНажмите на кнопку "Ввести данные"',
        reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data == "waiting_for_consent")
async def process_ask_for_consent(callback_query: CallbackQuery, state: FSMContext):
    keyboard = get_inline_keyboard_yes_no()
    await state.set_state(Registration.waiting_for_consent)
    await callback_query.message.answer("Я согласен на обработку персональных данных",
                                        reply_markup=keyboard)
    await callback_query.answer()


@router.callback_query(Registration.waiting_for_consent, lambda c: c.data in ["yes", "no"])
async def process_choose_yes_or_no(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == "yes":
        await state.set_state(Registration.last_name)
        await callback_query.message.answer("Введите вашу фамилию (только русские символы):")
        await callback_query.answer()

    else:
        await callback_query.message.delete()
        await callback_query.message.answer(
            f"Очень жаль. Надеемся, Вы передумаете.",
            reply_markup=get_inline_keyboard_enter_data()
            )
        await callback_query.answer()
        await state.clear()


@router.message(Registration.last_name)
async def process_input_last_name(message: Message,  state: FSMContext):
    if not await validate_string(message):
        await message.answer("только русские символы")
        return

    await state.update_data(last_name=message.text.strip())
    await state.set_state(Registration.first_name)
    await message.answer("Введите ваше имя (только русские символы):")


@router.message(Registration.first_name)
async def process_input_first_name(message: Message,  state: FSMContext):
    if not await validate_string(message):
        await message.answer("только русские символы")
        return

    await state.update_data(first_name=message.text.strip())
    await state.set_state(Registration.middle_name)
    await message.answer("Введите ваше отчество (только русские символы):")


@router.message(Registration.middle_name)
async def process_input_middle_name(message: Message,  state: FSMContext):
    if not await validate_string(message):
        await message.answer("только русские символы")
        return

    await state.update_data(middle_name=message.text.strip())
    data = await state.get_data()
    telegram_id, full_name, full_name_from_tg, username = await get_data_user(message, data)
    full_name = await normalize_full_name(full_name)

    user = await get_user_by_id(telegram_id=telegram_id)
    if user:
        if user.is_active is True:
            await message.answer("Ваша заявка уже обрабатывается Администратором")
            return
        elif user.is_active is False:
            await update_is_active_user_by_id(telegram_id=telegram_id, full_name=full_name)
    else:
        await save_user(
            telegram_id=telegram_id,
            full_name=full_name,
            full_name_from_tg=full_name_from_tg,
            username=username
        )

    # Отправка письма в фоновом режиме с логированием результата
    task = asyncio.create_task(send_email(telegram_id, full_name, full_name_from_tg, username))
    task.add_done_callback(lambda t: logger.info("Фоновая задача завершена успешно. Письмо отправленно")
                           if t.exception() is None else
                           logger.error(f"Ошибка в задаче: {t.exception()}"))

    keyboards = get_button_reg()
    await message.answer(
        f"""Спасибо!\nЧтобы зарегистрироваться, нажмите на кнопку Регистрация.\nВаш запрос будет обработан Администратором.""",
        reply_markup=keyboards
    )

    # Проверка включения пользователя в группу фоновом режиме и отправкой об успешном добавлении
    asyncio.create_task(check_user_in_group_and_notify(user_id=telegram_id, message=message))

    await state.clear()
