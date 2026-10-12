"""Скачивание MP3 по URL и отправка в Telegram."""

import logging

import aiohttp
from aiogram.types import BufferedInputFile, Message

from config import SITE1_HEADERS
from utils.filename import extract_filename, split_performer_title
from utils.id3 import read_cover, read_id3_tags

MAX_AUDIO_SIZE = 50 * 1024 * 1024    # 50 МБ — лимит Telegram на аудио
MAX_COVER_SIZE = 200 * 1024          # 200 КБ — лимит Telegram на обложку


async def _download_audio(url: str) -> tuple[bytes, str] | None:
    """Скачивает MP3. Возвращает (байты, имя файла) или None при ошибке."""
    async with aiohttp.ClientSession(headers=SITE1_HEADERS) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            content_type = resp.headers.get("Content-Type", "")
            if "audio" not in content_type:
                return None
            filename = extract_filename(url, resp.headers)
            return await resp.read(), filename


async def _download_cover(cover_url: str) -> bytes | None:
    """Скачивает обложку по URL. None, если не получилось или она слишком большая."""
    try:
        async with aiohttp.ClientSession(headers=SITE1_HEADERS) as session:
            async with session.get(cover_url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.read()
                if len(data) > MAX_COVER_SIZE:
                    logging.info("Обложка слишком большая: %d байт", len(data))
                    return None
                return data
    except Exception:
        logging.exception("Не удалось скачать обложку")
        return None


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
    url: str,
    performer: str | None = None,
    title: str | None = None,
    cover_url: str | None = None,
) -> None:
    """Скачивает MP3 по URL и отправляет его в чат."""
    result = await _download_audio(url)
    if not result:
        await message.answer(
            "Не удалось скачать. Возможно, ссылка требует премиум-доступа."
        )
        return

    audio_bytes, filename = result

    if len(audio_bytes) > MAX_AUDIO_SIZE:
        await message.answer("Файл больше 50 МБ, Telegram не примет 😔")
        return

    performer, title = _resolve_metadata(audio_bytes, filename, performer, title)

    cover_bytes = await _download_cover(cover_url) if cover_url else None
    cover_bytes = _resolve_cover(audio_bytes, cover_bytes)

    thumbnail = (
        BufferedInputFile(cover_bytes, filename="cover.jpg")
        if cover_bytes else None
    )

    logging.info(
        "Отправляю: filename=%r, performer=%r, title=%r, cover=%s bytes",
        filename, performer, title, len(cover_bytes) if cover_bytes else 0,
    )

    audio = BufferedInputFile(audio_bytes, filename=filename)
    await message.answer_audio(
        audio=audio,
        title=title or None,
        performer=performer or None,
        thumbnail=thumbnail,
    )