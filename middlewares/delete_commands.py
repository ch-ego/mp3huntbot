"""Middleware: удаляет входящие команды (кроме /start) и убирает сервисные сообщения бота."""

import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

from services.ui_cache import pop_all

# Команды, которые НЕ удаляем из чата
KEEP_COMMANDS = {"/start"}


class DeleteCommandsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        if event.text:
            user_id = event.from_user.id if event.from_user else None

            # Проверяем, не в списке ли исключений
            cmd = event.text.split()[0].split("@")[0] if event.text.startswith("/") else None

            if cmd and cmd not in KEEP_COMMANDS:
                try:
                    await event.delete()
                except Exception:
                    logging.debug("Не удалось удалить команду %r", event.text)

            # Убираем сервисные сообщения бота (справку и т.п.)
            if user_id:
                for msg_id in pop_all(user_id):
                    try:
                        await event.bot.delete_message(event.chat.id, msg_id)
                    except Exception:
                        logging.debug("Не удалось удалить сервисное сообщение %d", msg_id)

        return await handler(event, data)