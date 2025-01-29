import asyncio
import logging
import sys

from init_bot import dp, bot

from logs.logging_config import logger
from handlers import handlers
from utils.utils import kick_user_from_channel


async def main():
    polling_task = asyncio.create_task(dp.start_polling(bot))
    kick_task = asyncio.create_task(kick_user_from_channel())

    try:
        await asyncio.gather(polling_task, kick_task)
    except asyncio.CancelledError:
        pass
    finally:
        kick_task.cancel()
        polling_task.cancel()

if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Выход")
    except Exception as e:
        logger.exception(f"Критическая ошибка: {e}")
