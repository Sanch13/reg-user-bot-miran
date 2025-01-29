import asyncio
import time

import aiosmtplib
from email.message import EmailMessage

from aiogram.types import Message
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from config import settings
from init_bot import bot
from logs.logging_config import logger
from queue_handlers.handlers import get_from_queue


async def send_email(telegram_id, full_name, full_name_from_tg, username):
    """
    Отправляет  письмо администратором о регистрации нового пользователя
    """
    message = EmailMessage()
    message["From"] = settings.SENDER_EMAIL
    message["To"] = settings.TO_EMAILS
    message["Subject"] = "Новая регистрация в телеграм Канале"

    # HTML-разметка для письма
    html_content = f"""
        <html>
            <body>
                <h1>Новая регистрация в телеграм Канале</h1>
                <p><strong>Telegram ID:</strong> {telegram_id}</p>
                <p><strong>Введенное ФИО при регистрации:</strong> {full_name}</p>
                <p><strong>Полное имя из Telegram:</strong> {full_name_from_tg}</p>
                <p><strong>Username из Telegram:</strong> {username}</p>
            </body>
        </html>
        """

    # Устанавливаем HTML-разметку как содержимое письма
    message.set_content(html_content, subtype='html')

    try:
        await aiosmtplib.send(message,
                              hostname=settings.SMTP_SERVER,
                              port=587,
                              start_tls=True,
                              username=settings.SENDER_EMAIL,
                              password=settings.PASSWORD)
        logger.info(f"Письмо успешно отправлено на адрес {settings.TO_EMAILS}!")
    except asyncio.TimeoutError:
        logger.error("Ошибка: время ожидания истекло при подключении или отправке письма.")
    except Exception as e:
        logger.exception(f"Ошибка при отправке письма: {e}")


async def send_email_that_user_delete_from_chanel(full_name, telegram_id):
    """
    Отправляет  письмо администратором о удалении пользователя с канала
    """
    message = EmailMessage()
    message["From"] = settings.SENDER_EMAIL
    message["To"] = settings.TO_EMAILS
    message["Subject"] = "Удаление пользователя из телеграм Канала"

    # HTML-разметка для письма
    html_content = f"""
            <html>
                <body>
                    <h1>Удаление пользователя из телеграм Канала</h1>
                    <p>
                    Пользователь <strong>{full_name}</strong>  c 
                    <strong>Telegram ID: {telegram_id}</strong> 
                    успешно удален из телеграм канала.
                    </p>
                </body>
            </html>
            """

    # Устанавливаем HTML-разметку как содержимое письма
    message.set_content(html_content, subtype='html')

    try:
        await aiosmtplib.send(message,
                              hostname=settings.SMTP_SERVER,
                              port=587,
                              start_tls=True,
                              username=settings.SENDER_EMAIL,
                              password=settings.PASSWORD)
        logger.info(f"Письмо успешно отправлено на адрес {settings.TO_EMAILS}!")
    except asyncio.TimeoutError:
        logger.error("Ошибка: время ожидания истекло при подключении или отправке письма.")
    except Exception as e:
        logger.exception(f"Ошибка при отправке письма: {e}")


async def get_data_user(message: Message, data: dict) -> tuple:
    """
    Формирует данные пользователя в tuple
    """
    return (
        message.from_user.id,
        f"{data.get('last_name', '')} {data.get('first_name', '')} {data.get('middle_name', '')}",
        message.from_user.full_name or "",
        message.from_user.username or ""
    )


async def normalize_full_name(full_name: str) -> str:
    """
    Нормализует ФИО к виду: Иванов Иван Иванович
    :param full_name:
    :return:
    """
    return full_name.title()


#  проверка на добавление пользователя в группу и ответ пользователю
async def is_user_in_group(user_id: int) -> bool:
    """
    Проверяет существует ли пользователь в группе
    """
    try:
        member = await bot.get_chat_member(chat_id=settings.CHANNEL_ID_MIRAN, user_id=user_id)
        return member.status in ('member', 'creator', 'administrator')
    except (TelegramForbiddenError, TelegramBadRequest) as e:
        logger.error(f"Ошибка проверки пользователя {user_id}: {e}")
        return False


async def check_user_in_group_and_notify(user_id: int, message: Message, max_attempts: int = 100):
    """
    Уведомляет пользователя об успешной подписке в группу. Таймаут = 1 час.
    После истечения этого времени уведомления не будет.
    """
    attempts = 0
    while attempts < max_attempts:
        if await is_user_in_group(user_id):
            await message.answer("Вы успешно добавлены в Telegram-канал МИРАН и можете пользоваться контентом!")
            return
        await asyncio.sleep(36)  # Проверять каждые 36 секунд
        attempts += 1


async def kick_user_from_channel(channel_id=settings.CHANNEL_ID_MIRAN):
    """Функция для обработки задач из очереди с периодичностью 30 секунд."""
    while True:
        try:
            task = await get_from_queue()
            if task:
                telegram_id = task.get("telegram_id")
                full_name = task.get("full_name")
                try:
                    # Блокируем и удаляем пользователя
                    await bot.ban_chat_member(
                        chat_id=channel_id,
                        user_id=telegram_id,
                        until_date=int(time.time()) - 30
                    )
                    logger.info(f"Пользователь {full_name} c {telegram_id} исключен из канала")
                    await asyncio.sleep(20)
                    # Сразу разблокируем
                    await bot.unban_chat_member(
                        chat_id=channel_id,
                        user_id=telegram_id
                    )
                    logger.info(f"Пользователь {full_name} c {telegram_id} разблокирован!!!")
                    await asyncio.sleep(5)
                    await send_email_that_user_delete_from_chanel(full_name, telegram_id)
                except Exception as e:
                    logger.exception(f"Ошибка при кике {full_name}: {e}")
            else:
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            logger.info("Задача кика пользователей остановлена")
            raise
        except Exception as e:
            logger.exception(f"Неожиданная ошибка: {e}")
            await asyncio.sleep(10)
