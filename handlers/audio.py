import logging

from aiogram import F, Router
from aiogram.types import Message

from config import URL_PATTERN
from services.audio_sender import send_audio_from_url

router = Router()


@router.message(F.text.regexp(URL_PATTERN))
async def send_audio_by_url(message: Message):
    url = message.text.strip()
    await message.answer("Сейчас отправлю трек 🎵")
    await send_audio_from_url(message, url)