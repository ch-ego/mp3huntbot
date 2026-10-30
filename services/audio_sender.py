"""Скачивание MP3 по URL и отправка в Telegram."""

import logging

from aiogram.types import BufferedInputFile, Message
from services.limits import download_semaphore
from sources.registry import get_source
from utils.filename import  split_performer_title
from utils.id3 import read_cover, read_id3_tags

MAX_AUDIO_SIZE = 50 * 1024 * 1024    # 50 МБ — лимит Telegram на аудио
MAX_COVER_SIZE = 200 * 1024          # 200 КБ — лимит Telegram на обложку


# ---------- Вспомогательные функции ----------
async def _send_audio_inner(message: Message, track: dict) -> None:
    """Скачивает MP3 через нужный источник, читает метаданные, отправляет аудио с обложкой."""

    # 1. Определяем, с какого сайта трек (по умолчанию site1)
    source_id = track.get("source", "site1")
    source = get_source(source_id)

    # 2. Просим источник скачать аудио
    result = await source.download_audio(track["url"])
    if not result:
        await message.answer("Не удалось скачать файл с сайта. Возможно, он временно недоступен.")
        return

    audio_bytes, filename = result

    if len(audio_bytes) > MAX_AUDIO_SIZE:
        await message.answer("Файл больше 50 МБ, Telegram не примет 😔")
        return

    # 3. Просим источник скачать обложку (если ссылка на неё есть)
    cover_bytes = None
    if track.get("cover_url"):
        cover_bytes = await source.download_cover(track["cover_url"])

    # 4. Если обложки нет, пробуем достать из ID3
    cover_bytes = _resolve_cover(audio_bytes, cover_bytes)

    # 5. Определяем performer и title
    # Берем их из словаря track (если они там есть), иначе достаем из ID3
    performer, title = _resolve_metadata(
        audio_bytes,
        filename,
        track.get("artist"),
        track.get("title")
    )

    # 6. Формируем файлы для Telegram
    thumbnail = (
        BufferedInputFile(cover_bytes, filename="cover.jpg")
        if cover_bytes else None
    )
    audio = BufferedInputFile(audio_bytes, filename=filename)

    logging.info(
        "Отправляю: filename=%r, performer=%r, title=%r, cover=%s bytes",
        filename, performer, title, len(cover_bytes) if cover_bytes else 0,
    )

    # 7. Отправляем
    await message.answer_audio(
        audio=audio,
        title=title or None,
        performer=performer or None,
        thumbnail=thumbnail,
    )


def _resolve_metadata(
    audio_bytes: bytes,
    filename: str,
    performer: str | None,
    title: str | None,
) -> tuple[str | None, str]:
    """Определяет performer и title: сначала переданные, потом ID3, потом имя файла."""
    if not performer and not title:
        id3_performer, id3_title = read_id3_tags(audio_bytes)
        performer = performer or id3_performer
        title = title or id3_title

    if not performer and not title:
        performer, title = split_performer_title(filename)

    return performer, title or filename


def _resolve_cover(audio_bytes: bytes, cover_bytes: bytes | None) -> bytes | None:
    """Обложка: сначала из URL, если нет — из ID3."""
    if cover_bytes:
        return cover_bytes

    id3_cover = read_cover(audio_bytes)
    if id3_cover and len(id3_cover) <= MAX_COVER_SIZE:
        return id3_cover
    return None


async def send_audio_from_url(
    message: Message,
    track: dict,
) -> None:
    """Скачивает MP3 по URL и отправляет в чат. Ограничена семафором."""
    async with download_semaphore:
        await _send_audio_inner(message, track)