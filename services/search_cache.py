"""In-memory кэш результатов поиска: один активный поиск на пользователя."""

import uuid

_cache: dict[int, tuple[str, list[dict]]] = {}


def save_tracks(user_id: int, tracks: list[dict]) -> str:
    """Сохраняет треки и возвращает уникальный search_id."""
    search_id = uuid.uuid4().hex[:8]
    _cache[user_id] = (search_id, tracks)
    return search_id


def get_tracks(user_id: int, search_id: str) -> list[dict] | None:
    """Возвращает треки, если search_id совпадает с актуальным."""
    entry = _cache.get(user_id)
    if not entry:
        return None
    saved_id, tracks = entry
    if saved_id != search_id:
        return None
    return tracks


def clear(user_id: int) -> None:
    _cache.pop(user_id, None)