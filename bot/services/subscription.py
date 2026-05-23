"""Channel subscription service."""
import logging
from typing import List
from aiogram import Bot
from aiogram.types import ChatMemberStatus
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger('bot')

MEMBER_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.CREATOR,
}


async def is_subscribed_to_all(bot: Bot, user_id: int, channels: List[str] = None) -> bool:
    """Check if user is subscribed to all required channels."""
    channels = channels or settings.REQUIRED_CHANNELS
    if not channels:
        return True

    cache_key = f"sub_check:{user_id}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    for channel in channels:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in MEMBER_STATUSES:
                cache.set(cache_key, False, timeout=30)
                return False
        except Exception as e:
            logger.warning(f"Cannot check {channel} for {user_id}: {e}")
            return False

    cache.set(cache_key, True, timeout=300)
    return True


async def invalidate_subscription_cache(user_id: int):
    """Invalidate subscription cache for user."""
    cache.delete(f"sub_check:{user_id}")
