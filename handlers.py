from aiogram import types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from init_bot import router
from middleware import check_subscribe, check_registration
from utils import delivery
from utils_for_db import add_user
from keyboards import get_inline_keyboard, get_inline_keyboard_yes_no


class Registration(StatesGroup):
    name_parent = State()
    name_child = State()
    age_child = State()
    add_more_children = State()
    delivery = State()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    keyboard = get_inline_keyboard()
    await message.answer(
        text=f"Пожалуйста, проверьте вашу подписку на наш корпоративный Telegram-канал\n" \
             f"""Чтобы зарегистрироваться, пожалуйста, нажмите кнопку "Регистрация" """,
        reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data == "registration")
@check_subscribe
@check_registration
async def participate_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(Registration.name_parent)
    await callback_query.message.answer("Введите ваше ФИО")
    await callback_query.answer()


@router.message(Registration.name_parent)
async def process_name_parent(message: Message, state: FSMContext):
    await state.update_data(name_parent=message.text.strip())
    await state.set_state(Registration.name_child)
    await message.answer(f"""Введите ФИО ребёнка""")


@router.message(Registration.name_child)
async def process_name_child(message: Message, state: FSMContext):
    await state.update_data(current_name_child=message.text.strip())
    await state.set_state(Registration.age_child)
    await message.answer("Введите возраст ребёнка (числовое значение)")


@router.message(Registration.age_child)
async def process_age_child(message: Message, state: FSMContext):
    data = await state.get_data()
    children = data.get("children", [])
    current_name_child = data.get("current_name_child")

    try:
        age_child = int(message.text.strip())
        children.append({
            "name": current_name_child,
            "age": age_child,
        })

        await state.update_data(children=children)
        await state.set_state(Registration.add_more_children)
        await message.answer("Хотите добавить ещё одного ребёнка?",
                             reply_markup=get_inline_keyboard_yes_no())

    except ValueError:
        await message.answer("Пожалуйста, введите числовое значение")
        return


@router.callback_query(Registration.add_more_children, lambda c: c.data in ["yes", "no"])
async def process_add_more_children(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == "yes":
        await state.set_state(Registration.name_child)
        await callback_query.message.answer("Введите ФИО ребёнка")
        await callback_query.answer()

    else:
        await state.set_state(Registration.delivery)
        await callback_query.message.answer(f"""
        Пожалуйста, укажите предпочитаемый способ доставки на мероприятие (туда и обратно)
        1. от ст. метро Институт Культуры (через Самохваловичи)
        2. от ст. метро Могилёвская
        3. от ст. метро Уручье
        4. самостоятельно  
        Введите номер (1 - 4)
""")
        await callback_query.answer()


@router.message(Registration.delivery)
async def process_delivery(message: Message, state: FSMContext):
    user_id = message.from_user.id
    number_delivery = message.text.strip()

    if number_delivery in ('1', '2', '3', '4'):
        await state.update_data(delivery=number_delivery)
    else:
        await message.answer("Пожалуйста, введите числовое значение (1 - 4)")
        return

    data = await state.get_data()
    for obj in data.get("children"):
        await add_user(
            user_id=user_id,
            name_parent=data.get('name_parent'),
            name_child=obj.get('name'),
            age_child=obj.get('age'),
            delivery=delivery.get(data.get('delivery')),
            delivery_id=int(data.get('delivery'))
        )

    await state.clear()
    await message.answer("Спасибо, регистрация успешно пройдена. Ждём вас на мероприятии")
