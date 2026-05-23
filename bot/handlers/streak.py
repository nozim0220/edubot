"""Streak tizimi — har kuni faollik."""
import logging
from datetime import date, timedelta
from aiogram import Router
from asgiref.sync import sync_to_async

router = Router()
logger = logging.getLogger('bot')


async def update_streak(user) -> dict:
    """
    Foydalanuvchi har kirganida streak yangilanadi.
    Returns: {'streak': int, 'is_new_day': bool, 'bonus_xp': int}
    """
    try:
        result = await sync_to_async(_update_streak_sync)(user)
        return result
    except Exception as e:
        logger.debug(f"Streak update: {e}")
        return {'streak': 0, 'is_new_day': False, 'bonus_xp': 0}


def _update_streak_sync(user) -> dict:
    from apps.users.models import User
    from django.utils import timezone

    u = User.objects.get(pk=user.pk)
    today = date.today()

    last_active = getattr(u, 'last_active_date', None)
    streak = getattr(u, 'streak_days', 0) or 0

    is_new_day = False
    bonus_xp   = 0

    if last_active is None:
        # Birinchi marta
        streak    = 1
        is_new_day= True
    elif last_active == today:
        # Bugun allaqachon kirgan
        pass
    elif last_active == today - timedelta(days=1):
        # Kecha kirgan — streak davom etadi
        streak    += 1
        is_new_day = True
    else:
        # 1+ kun o'tgan — streak nolga
        streak    = 1
        is_new_day= True

    if is_new_day:
        bonus_xp = 10 + min(streak * 5, 100)  # streak oshgan sari ko'proq XP
        User.objects.filter(pk=u.pk).update(
            last_active_date=today,
            streak_days=streak,
        )
        # XP qo'shish
        try:
            u.add_xp(bonus_xp)
        except Exception:
            pass

    return {'streak': streak, 'is_new_day': is_new_day, 'bonus_xp': bonus_xp}


def get_streak_emoji(streak: int) -> str:
    if streak >= 30: return "🔥🔥🔥"
    if streak >= 14: return "🔥🔥"
    if streak >= 7:  return "🔥"
    if streak >= 3:  return "✨"
    return "⭐"