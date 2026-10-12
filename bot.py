import asyncio
import logging
import os

from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Включаем логирование, чтобы видеть, что происходит
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        f"Я твой первый бот на aiogram 3."
    )


# Хэндлер на команду /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Доступные команды:\n/start — приветствие\n/help — эта справка")


# Эхо-хэндлер: отвечает на любое текстовое сообщение
@dp.message(F.text)
async def echo(message: Message):
    await message.answer(f"Ты написал: {message.text}")


# Точка входа
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")