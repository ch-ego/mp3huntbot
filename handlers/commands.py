from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        f"Кидай мне ссылку на .mp3 — отправлю трек."
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Доступные команды:\n"
        "/start — приветствие\n"
        "/search — поиск\n"
        "/help — эта справка\n\n"
        "Или просто пришли ссылку на .mp3-файл."
    )
