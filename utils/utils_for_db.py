from sqlalchemy import exists, join
from sqlalchemy.future import select

from models.database import AsyncSession
from models.models import User, Lottery, Ticket


async def is_exists_user(telegram_id: int) -> bool:
    """
    Функция для проверки существования в БД пользователя по telegram_id
    :param telegram_id:
    :return: true or false:
    """
    async with AsyncSession() as session:
        # Создание запроса на проверку существования
        query = select(exists().where(User.telegram_id == telegram_id))
        result = await session.execute(query)  # Выполнение запроса
        return result.scalar()  # Получение результата (True или False)


async def save_user(telegram_id: int, full_name: str, full_name_from_tg: str) -> None:
    """
    Функция для сохранения пользователя в БД
    :param telegram_id:
    :param full_name:
    :return: None:
    """
    async with AsyncSession() as session:
        new_user = User(
            telegram_id=telegram_id,
            full_name=full_name,
            full_name_from_tg=full_name_from_tg
        )  # Создаём новый объект User

        session.add(new_user)  # Добавляем его в сессию
        await session.commit()  # Сохраняем изменения


async def get_lottery_data(name):
    """
    Получить данные о пользователях и билетах для определенной лотереи.
    :param name: Название лотереи.
    :return: Список с данными пользователей и их билетами.
    """
    async with AsyncSession() as session:
        query = (
            select(
                User.telegram_id,
                User.full_name,
                User.full_name_from_tg,
                Lottery.name,
                Ticket.ticket_number
            )
            .select_from(
                join(Ticket, User, Ticket.user_id == User.id)  # Объединение Ticket с User
                .join(Lottery, Ticket.lottery_id == Lottery.id)  # Объединение с Lottery
            ).where(Lottery.name == name)
        )

        # Выполняем запрос
        result = await session.execute(query)

        # Извлекаем все данные
        data = result.fetchall()

        # Преобразуем результат в список словарей
        result_data = [
            {
                "telegram_id": row.telegram_id,
                "full_name": row.full_name,
                "full_name_from_tg": row.full_name_from_tg,
                "lottery_name": row.name,
                "ticket_number": row.ticket_number
            }
            for row in data
        ]
        return result_data
