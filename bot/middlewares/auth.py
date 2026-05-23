"""Auth middleware — optimallashtirilgan, tez."""
import logging, time
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from asgiref.sync import sync_to_async

logger = logging.getLogger('bot')

_user_cache: dict = {}
CACHE_TTL = 60  # 60 soniya — ko'proq cache


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user = None
        if isinstance(event, (Message, CallbackQuery)):
            tg_user = event.from_user

        if not tg_user:
            data['user'] = None
            data['is_new_user'] = False
            return await handler(event, data)

        tg_id = tg_user.id
        now   = time.time()

        # Cache dan olish
        cached = _user_cache.get(tg_id)
        if cached and (now - cached['ts']) < CACHE_TTL:
            data['user'] = cached['user']
            data['is_new_user'] = False
            if cached['user'] and getattr(cached['user'], 'status', '') == 'banned':
                if isinstance(event, Message):
                    await event.answer("🚫 Bloklangansiz.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("🚫 Bloklangansiz.", show_alert=True)
                return
            return await handler(event, data)

        # DB dan olish — faqat cache yo'q bo'lsa
        try:
            user, created = await sync_to_async(_get_or_create_user)(
                tg_id,
                tg_user.username or '',
                tg_user.first_name or '',
                tg_user.last_name or '',
            )
            _user_cache[tg_id] = {'user': user, 'ts': now}
            data['user'] = user
            data['is_new_user'] = created

            if user and getattr(user, 'status', '') == 'banned':
                if isinstance(event, Message):
                    await event.answer("🚫 Bloklangansiz.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("🚫 Bloklangansiz.", show_alert=True)
                return

        except Exception as e:
            logger.error(f"Auth: {e}")
            data['user'] = None
            data['is_new_user'] = False

        return await handler(event, data)


def _get_or_create_user(tg_id, username, first_name, last_name):
    """Sinxron DB — thread da ishlaydi."""
    from apps.users.services import TelegramAuthService
    return TelegramAuthService.get_or_create_user({
        'id': tg_id,
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
    })


def invalidate_user_cache(tg_id: int):
    _user_cache.pop(tg_id, None)