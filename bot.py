import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import audio, commands, search
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.fsm.storage.memory import MemoryStorage

# --- Загрузка переменных и логирование ---
load_dotenv()
logging.basicConfig(level=logging.INFO)

# --- Бот и диспетчер ---
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())

# 2. ОБЯЗАТЕЛЬНО подключаем роутеры к диспетчеру
dp.include_router(audio.router)
dp.include_router(commands.router)
dp.include_router(search.router)

# 3. Прописываем команды
async def set_bot_commands(bot: Bot):
    """Устанавливает список команд для меню бота."""
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Показать справку"),
        BotCommand(command="search", description="Найти музыку по названию"),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
# ---------- Точка входа ----------

async def main():
    print("Бот запущен...")
    await set_bot_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")