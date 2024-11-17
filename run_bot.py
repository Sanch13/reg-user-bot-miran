import asyncio

from init_bot import dp, bot
from utils_for_db import create_db
from utils import setup_scheduler
from logging_config import logger
import handlers


async def main():
    setup_scheduler()
    await create_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Выход")
    except Exception as error:
        logger.error("Exception occurred: {}", error)
