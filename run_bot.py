import asyncio
import logging
import sys

from init_bot import dp, bot

# from utils_for_db import create_db
# from utils import setup_scheduler

from logs.logging_config import logger


async def main():
    # setup_scheduler()
    # await create_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Выход")
    except Exception as error:
        logger.error("Exception occurred: {}", error)
