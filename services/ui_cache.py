"""In-memory кэш сервисных сообщений бота, которые нужно удалить при следующей команде."""

_ephemeral: dict[int, list[int]] = {}


def track(user_id: int, message_id: int) -> None:
    """Добавляет message_id в список на удаление при следующей команде пользователя."""
    _ephemeral.setdefault(user_id, []).append(message_id)


def pop_all(user_id: int) -> list[int]:
    """Забирает все message_id пользователя и очищает список."""
    return _ephemeral.pop(user_id, [])