import logging
import aiohttp
from aiogram import Router, F
from aiogram.types import BufferedInputFile, Message

from config import MUSIFY_HEADERS, URL_PATTERN
from utils.filename import extract_filename, split_performer_title
from utils.id3 import read_id3_tags, read_cover

router = Router()

@router.message(F.text.regexp(URL_PATTERN))
async def send_audio_by_url(message: Message):
    url = message.text.strip()
    await message.answer("Сейчас отправлю трек 🎵")

    try:
        async with aiohttp.ClientSession(headers=MUSIFY_HEADERS) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await message.answer(
                        f"Сайт отдал ошибку {resp.status}. "
                        f"Скорее всего, ссылка требует премиум-доступа."
                    )
                    return

                content_type = resp.headers.get("Content-Type", "")
                if "audio" not in content_type:
                    await message.answer(
                        "По ссылке не аудио, а что-то другое."
                    )
                    return

                filename = extract_filename(url, resp.headers)
                audio_bytes = await resp.read()

        if len(audio_bytes) > 50 * 1024 * 1024:
            await message.answer("Файл больше 50 МБ, Telegram не примет 😔")
            return

        # 1. Пробуем ID3-теги
        performer, title = read_id3_tags(audio_bytes)

        # 2. Обложка
        cover_bytes = read_cover(audio_bytes)

        thumbnail = None
        if cover_bytes and len(cover_bytes) < 200 * 1024:
            thumbnail = BufferedInputFile(cover_bytes, filename="cover.jpg")


        # 3. Если тегов нет — fallback на имя файла
        if not performer and not title:
            performer, title = split_performer_title(filename)

        logging.info(
            "Отправляю: performer=%r, title=%r, cover=%s bytes",
            performer, title, len(cover_bytes) if cover_bytes else 0,
        )

        audio = BufferedInputFile(audio_bytes, filename=filename)
        await message.answer_audio(
            audio=audio,
            title=title or None,
            performer=performer or None,
            thumbnail=thumbnail,
        )

    except Exception as e:
        logging.exception("Ошибка при отправке аудио")
        await message.answer(f"Не получилось: {e}")
