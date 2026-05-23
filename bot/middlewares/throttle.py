"""Rate limiting middleware."""
import logging
import time
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

logger = logging.getLogger('bot')


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 0.3):
        self.rate_limit = rate_limit
        self._user_timestamps: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id = None
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id if event.from_user else None

        if user_id:
            now = time.time()
            last = self._user_timestamps.get(user_id, 0)
            if now - last < self.rate_limit:
                if isinstance(event, CallbackQuery):
                    await event.answer("⏳ Iltimos kuting...", show_alert=False)
                return
            self._user_timestamps[user_id] = now

        return await handler(event, data)