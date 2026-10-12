from io import BytesIO
import logging
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from .encoding import try_fix_cp1251
import re

def is_meaningful(s: str | None) -> bool:
    """Проверяет, есть ли в строке хоть что-то осмысленное."""
    if not s:
        return False
    # только ?, пробелы и пунктуация — считаем мусором
    return bool(re.search(r"[A-Za-zА-Яа-я0-9]", s))

def read_id3_tags(audio_bytes: bytes) -> tuple[str | None, str | None]:
    """
    Читает ID3-теги из MP3.
    Возвращает (performer, title). None, если тегов нет.
    """
    try:
        audio = MP3(BytesIO(audio_bytes), ID3=ID3)
    except Exception:
        logging.exception("Не удалось прочитать ID3")
        return None, None

    def get_text(frame_id: str) -> str | None:
        if not audio.tags:
            return None
        frame = audio.tags.get(frame_id)
        if frame is None or not getattr(frame, "text", None):
            return None
        raw = str(frame.text[0])
        return try_fix_cp1251(raw)

    performer = get_text("TPE1")   # Artist
    title = get_text("TIT2")       # Title

    if not is_meaningful(performer):
        performer = None
    if not is_meaningful(title):
        title = None

    return performer, title

def read_cover(audio_bytes: bytes) -> bytes | None:
    """Достаёт обложку из ID3 (APIC-фрейм). Возвращает байты картинки или None."""
    try:
        audio = MP3(BytesIO(audio_bytes), ID3=ID3)
    except Exception:
        return None

    if not audio.tags:
        return None

    # В файле может быть несколько APIC — берём первый (обычно front cover)
    for frame in audio.tags.getall("APIC"):
        if frame.data:
            return frame.data
    return None