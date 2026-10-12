import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers.audio import router as audio_router
from handlers.commands import router as commands_router

# --- Загрузка переменных и логирование ---
load_dotenv()
logging.basicConfig(level=logging.INFO)

# --- Бот и диспетчер ---
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# 2. ОБЯЗАТЕЛЬНО подключаем роутеры к диспетчеру
dp.include_router(audio_router)
dp.include_router(commands_router)

# ---------- Точка входа ----------

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")