from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from services.ui_cache import track

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        f"Кидай мне ссылку на .mp3 — отправлю трек."
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    sent = await message.answer(
        "Доступные команды:\n"
        "/search — найти музыку\n"
        "/help — эта справка\n"
    )
    track(message.from_user.id, sent.message_id)
