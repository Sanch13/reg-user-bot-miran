Чтобы настроить взаимодействие между Django и ботом через очередь на Redis, выполните следующие шаги:

---

### **1. Настройка Redis на сервере**
Убедитесь, что Redis работает на вашем сервере:

1. **Проверьте статус Redis:**
   ```bash
   sudo systemctl status redis
   ```
2. **Настройте доступ для Redis:**
   Redis по умолчанию работает на `localhost` (127.0.0.1). Если Django и бот находятся на одном сервере, настройки можно оставить по умолчанию.

---

### **2. Установите необходимые пакеты**
Установите `aioredis` для бота и `redis` для Django:

#### Для Django:
```bash
pip install redis
```

#### Для бота:
```bash
pip install aioredis
```

---

### **3. Настройка Django для отправки задач**
В Django-проекте создайте модуль для работы с Redis (например, `queue_handler.py`):

```python
import redis
import json

REDIS_HOST = "localhost"  # Адрес Redis-сервера
REDIS_PORT = 6379        # Порт Redis
QUEUE_NAME = "delete_queue"  # Название очереди

def add_to_queue(data):
    """Добавить задачу в очередь."""
    redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    redis_client.rpush(QUEUE_NAME, json.dumps(data))
```

Пример использования в Django:
```python
from myapp.queue_handler import add_to_queue

def delete_user(telegram_id):
    """Добавить задачу удаления пользователя в очередь."""
    task = {"telegram_id": telegram_id}
    add_to_queue(task)
    print(f"Задача на удаление пользователя {telegram_id} добавлена в очередь.")
```

Добавьте вызов этой функции при удалении пользователя из таблицы.

---

### **4. Настройка бота для обработки задач**
Дополните скрипт бота:

#### Основной обработчик очереди:
```python
import asyncio
import aioredis
import json
from aiogram import Bot
from dotenv import load_dotenv
import os

load_dotenv()

REDIS_HOST = "localhost"
REDIS_PORT = 6379
QUEUE_NAME = "delete_queue"
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
bot = Bot(token=os.getenv("API_TELEGRAM_TOKEN"))

async def process_task():
    """Обработка задач из очереди."""
    redis = await aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
    while True:
        task = await redis.lpop(QUEUE_NAME)  # Забираем задачу из очереди
        if task:
            data = json.loads(task)
            telegram_id = data.get("telegram_id")
            if telegram_id:
                try:
                    await bot.kick_chat_member(chat_id=CHANNEL_ID, user_id=telegram_id)
                    print(f"Пользователь {telegram_id} успешно удалён.")
                except Exception as e:
                    print(f"Ошибка при удалении пользователя {telegram_id}: {e}")
        else:
            await asyncio.sleep(1)  # Подождите перед следующей проверкой очереди
```

#### Основной скрипт для запуска:
```python
if __name__ == "__main__":
    asyncio.run(process_task())
```

---

### **5. Тестирование системы**
1. **Запустите Redis:**
   ```bash
   sudo systemctl start redis
   ```
2. **Запустите Django:**
   Django добавляет задачи в очередь через функцию `add_to_queue`.
3. **Запустите бота:**
   Бот обрабатывает задачи из очереди, выполняя запросы к Telegram API:
   ```bash
   python bot.py
   ```

---

### **6. Пример взаимодействия**
#### Django добавляет задачу:
```python
from myapp.queue_handler import add_to_queue

add_to_queue({"telegram_id": 123456789})
```

#### Бот обрабатывает задачу:
Бот слушает очередь `delete_queue`. Если появляется задача, он вызывает `bot.kick_chat_member`.

---

### **Что происходит:**
1. Django добавляет задачу удаления в очередь Redis.
2. Бот, работающий отдельно, периодически проверяет очередь.
3. Когда появляется новая задача, бот извлекает её и выполняет удаление пользователя из Telegram-канала.

---

### **Преимущества подхода:**
- **Изоляция компонентов:** Django и бот работают независимо друг от друга.
- **Масштабируемость:** Очередь можно использовать для других задач.
- **Асинхронность:** Redis позволяет обрабатывать задачи без задержек.

Если потребуется дополнительная настройка безопасности, например, шифрование данных в очереди, дайте знать!