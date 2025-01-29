import json

import redis.asyncio as redis

from config import settings

REDIS_HOST = settings.REDIS_HOST or "localhost"
REDIS_PORT = settings.REDIS_PORT or 6379
QUEUE_NAME = "telegram_deactivate_user_queue"


async def add_to_queue(data):
    """Добавить задачу в очередь."""
    r = redis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
    await r.rpush(QUEUE_NAME, json.dumps(data))
    await r.close()


async def get_from_queue():
    """Получить задачу из очереди."""
    r = redis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
    task = await r.lpop(QUEUE_NAME)
    await r.close()
    return json.loads(task) if task else None
