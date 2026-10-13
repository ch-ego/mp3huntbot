import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import audio, commands, search
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.fsm.storage.memory import MemoryStorage
from middlewares.delete_commands import DeleteCommandsMiddleware
from aiogram.client.session.aiohttp import AiohttpSession

# --- Загрузка переменных и логирование ---
load_dotenv()
logging.basicConfig(level=logging.INFO)

# Читаем адрес прокси из переменных окружения (по умолчанию - локальный)
proxy_url = os.getenv("PROXY_URL", "socks5://127.0.0.1:1443")

# --- Бот и диспетчер ---
session = AiohttpSession(proxy=proxy_url)
bot = Bot(token=os.getenv("BOT_TOKEN"), session=session)

dp = Dispatcher(storage=MemoryStorage())
dp.message.outer_middleware(DeleteCommandsMiddleware())

# 2. ОБЯЗАТЕЛЬНО подключаем роутеры к диспетчеру
dp.include_router(audio.router)
dp.include_router(commands.router)
dp.include_router(search.router)

# 3. Прописываем команды
async def set_bot_commands(bot: Bot):
    """Устанавливает список команд для меню бота."""
    commands = [
        BotCommand(command="search", description="Найти музыку по названию"),
        BotCommand(command="help", description="Показать справку"),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
# ---------- Точка входа ----------

async def main():
    try:
        await set_bot_commands(bot)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")