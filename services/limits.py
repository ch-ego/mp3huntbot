"""Лимиты: семафор на скачивание и rate limit на пользователя."""

import asyncio
import time
from collections import defaultdict, deque

from config import MAX_CONCURRENT_DOWNLOADS, RATE_LIMIT_MAX, RATE_LIMIT_WINDOW

# ---------- Семафор: ограничивает одновременные скачивания ----------
download_semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)

# ---------- Rate limit: сколько треков скачал каждый пользователь ----------
_user_downloads: dict[int, deque[float]] = defaultdict(deque)


def check_rate_limit(user_id: int) -> tuple[bool, int]:
    """
    Проверяет, не превышен ли лимит у пользователя.
    Возвращает (можно_ли_качать, сколько_секунд_ждать).
    """
    now = time.monotonic()
    timestamps = _user_downloads[user_id]

    # Убираем отметки, которые старше окна
    while timestamps and now - timestamps[0] > RATE_LIMIT_WINDOW:
        timestamps.popleft()

    if len(timestamps) >= RATE_LIMIT_MAX:
        wait = int(RATE_LIMIT_WINDOW - (now - timestamps[0])) + 1
        return False, wait

    timestamps.append(now)
    return True, 0