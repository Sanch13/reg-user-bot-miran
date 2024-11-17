import asyncio
import logging
import os
from datetime import date

import aiosmtplib
from contextlib import asynccontextmanager
from email.message import EmailMessage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import settings
from logging_config import logger


delivery = {
    '1': 'от ст. метро Институт Культуры (через Самохваловичи)',
    '2': 'от ст. метро Могилёвская',
    '3': 'от ст. метро Уручье',
    '4': 'самостоятельно'
}


async def get_excel_filename_today():
    return f"""Список_участников_на_{date.today()}.xlsx"""


async def get_path_to_excel_folder():
    from pathlib import Path

    base_dir = str(Path(__file__).resolve().parent)
    Path("excel").mkdir(exist_ok=True)
    excel_folder_path = base_dir + '/' + 'excel'
    return excel_folder_path


async def get_path_to_excel_file(excel_filename):
    return os.path.join(await get_path_to_excel_folder(), excel_filename)


async def send_email_with_attachment(subject: str = settings.SUBJECT,
                                     body: str = settings.BODY,
                                     from_email: str = settings.SENDER_EMAIL,
                                     to_email: str = settings.TO_EMAIL,
                                     to_emails: str = None):

    excel_file_path = await get_path_to_excel_file(excel_filename=await get_excel_filename_today())
    message = EmailMessage()
    message["From"] = from_email
    message["To"] = ", ".join(to_emails.split()) if to_emails else to_email
    message["Subject"] = subject
    message.set_content(body)

    with open(excel_file_path, "rb") as f:
        # vnd.openxmlformats-officedocument.spreadsheetml.sheet - only excel files
        message.add_attachment(f.read(),
                               maintype="application",
                               subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               # filename=await get_excel_filename_today())
                               filename=("utf-8", "", f"{await get_excel_filename_today()}"))

    await aiosmtplib.send(message,
                          hostname=settings.SMTP_SERVER,
                          port=587,
                          start_tls=True,
                          username=settings.SENDER_EMAIL,
                          password=settings.PASSWORD)


@asynccontextmanager
async def async_timeout(timeout):
    try:
        yield await asyncio.wait_for(asyncio.sleep(0), timeout=timeout)
    except asyncio.TimeoutError:
        logging.error("Operation timed out")


async def scheduled_task():
    from utils_for_db import save_all_data_to_excel, fetch_all_data

    try:
        logger.info("Starting scheduled task")

        # Шаг 1: Забираем данные с БД
        async with async_timeout(30):  # Таймаут на получение данных
            rows = await fetch_all_data()
            logger.info(f"Fetched {len(rows)} rows from the database")

        # Шаг 2: Сохраняем файл на диск
        async with async_timeout(30):  # Таймаут на сохранение файла
            await save_all_data_to_excel(rows=rows)
            logger.info("Data saved to Excel file")

        # Шаг 3: Отправляем письмо с файлом
        async with async_timeout(60):  # Таймаут на отправку письма
            await send_email_with_attachment(to_emails=settings.TO_EMAILS)
            logger.info(f"Email sent to {settings.TO_EMAILS}")

        logger.info("Scheduled task completed successfully")

    except Exception as e:
        logger.error(f"An error occurred: {e}")


def setup_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(scheduled_task, trigger=CronTrigger(hour=8, minute=0))
    scheduler.start()
