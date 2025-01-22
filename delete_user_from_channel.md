Понял! Вы хотите, чтобы ваш бот на основе `aiogram` слушал очередь задач и выполнял, например, удаление пользователей из Telegram-канала, используя метод `bot.kick_chat_member`. Вот как это можно реализовать.

---

### **1. Добавляем очередь задач**
Для очередей можно использовать библиотеку **Redis** в связке с **aio-pika** (RabbitMQ) или другой менеджер очередей. Здесь я покажу пример с использованием Redis и простого подхода.

Установите необходимые зависимости:
```bash
pip install redis aioredis
```

---

### **2. Настройка очереди на Redis**
Создайте файл `queue_handler.py` для работы с очередью:
```python
import aioredis
import json

REDIS_HOST = "localhost"  # Адрес Redis-сервера
REDIS_PORT = 6379        # Порт Redis
QUEUE_NAME = "delete_queue"  # Название очереди

async def add_to_queue(data):
    """Добавить задачу в очередь."""
    redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
    await redis.rpush(QUEUE_NAME, json.dumps(data))
    await redis.close()

async def get_from_queue():
    """Получить задачу из очереди."""
    redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
    task = await redis.lpop(QUEUE_NAME)
    await redis.close()
    return json.loads(task) if task else None
```

---

### **3. Логика обработки задач**
Дополняем ваш `bot.py`:

```python
import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot
from queue_handler import get_from_queue

load_dotenv()

bot = Bot(token=os.getenv("API_TELEGRAM_TOKEN"))
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")  # ID канала


async def process_task():
    """Функция для обработки задач из очереди."""
    while True:
        task = await get_from_queue()
        if task:
            telegram_id = task.get("telegram_id")
            try:
                await bot.kick_chat_member(chat_id=CHANNEL_ID, user_id=telegram_id)
                print(f"Пользователь {telegram_id} успешно удалён.")
            except Exception as e:
                print(f"Ошибка при удалении пользователя {telegram_id}: {e}")
        else:
            await asyncio.sleep(1)  # Ожидание перед повторной проверкой


async def main():
    """Основной цикл бота."""
    print("Бот запущен и слушает очередь...")
    await process_task()


if __name__ == "__main__":
    asyncio.run(main())
```

---

### **4. Добавление задачи в очередь**
Пример добавления задачи в очередь с другого сервиса:
```python
import asyncio
from queue_handler import add_to_queue

async def main():
    task = {"telegram_id": 123456789}
    await add_to_queue(task)
    print("Задача добавлена в очередь.")

if __name__ == "__main__":
    asyncio.run(main())
```

---

### **5. Запуск Redis**
Если Redis ещё не запущен, установите и запустите его:
```bash
sudo apt update
sudo apt install redis
sudo systemctl start redis
sudo systemctl enable redis
```

---

### **6. Что происходит:**
1. **Другой сервис** добавляет задачу (например, удаление пользователя) в Redis-очередь.
2. **Бот** постоянно слушает очередь (`delete_queue`) через `get_from_queue()`.
3. Когда появляется задача, бот вызывает `bot.kick_chat_member()` для выполнения действия.

---

### **Преимущества:**
- **Асинхронность:** Используется `aioredis`, который работает в асинхронной среде, подходящей для `aiogram`.
- **Изоляция:** Django или любой другой сервис только добавляет задачи, а бот обрабатывает их.
- **Простота:** Решение легко интегрировать и масштабировать.

Если нужно добавить обработку ошибок или улучшить систему, дайте знать!