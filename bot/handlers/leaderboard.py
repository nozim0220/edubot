"""Haftalik va umumiy reyting."""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async

router = Router()
logger = logging.getLogger('bot')

MEDALS = {1:"🥇", 2:"🥈", 3:"🥉"}


@router.message(F.text == "🏆 Reyting")
@router.callback_query(F.data == "menu:leaderboard")
async def leaderboard_menu(event, user, **kw):
    msg = event.message if isinstance(event, CallbackQuery) else event

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆 Umumiy reyting",  callback_data="lb:all"),
         InlineKeyboardButton(text="📅 Haftalik",        callback_data="lb:week")],
        [InlineKeyboardButton(text="🔥 Streak reyting",  callback_data="lb:streak")],
        [InlineKeyboardButton(text="🏠 Bosh menyu",      callback_data="menu:main")],
    ])
    try:
        await msg.edit_text("🏆 <b>Reyting</b>\n\nKategoriya tanlang:", reply_markup=kb)
    except Exception:
        await msg.answer("🏆 <b>Reyting</b>\n\nKategoriya tanlang:", reply_markup=kb)

    if isinstance(event, CallbackQuery):
        await event.answer()


@router.callback_query(F.data == "lb:all")
async def lb_all(cb: CallbackQuery, user, **kw):
    top = await sync_to_async(_get_top_xp)(20)
    text = "🏆 <b>Umumiy reyting (XP bo'yicha)</b>\n\n"
    for i, u in enumerate(top, 1):
        medal = MEDALS.get(i, f"{i}.")
        is_me = "👈" if u['tg_id'] == user.telegram_id else ""
        premium = "💎" if u.get('is_premium') else ""
        text += f"{medal} {premium}{u['name'][:20]} — <b>{u['xp']:,} XP</b> {is_me}\n"

    # O'zining o'rni
    my_rank = await sync_to_async(_get_my_rank)(user, 'xp')
    text += f"\n📍 Sizning o'rningiz: <b>#{my_rank}</b>"

    await cb.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:leaderboard")
        ]])
    )
    await cb.answer()


@router.callback_query(F.data == "lb:week")
async def lb_week(cb: CallbackQuery, user, **kw):
    top = await sync_to_async(_get_top_weekly)(20)
    text = "📅 <b>Haftalik reyting</b>\n\n"
    if not top:
        text += "Haftada hali hech kim ball to'plamagan."
    for i, u in enumerate(top, 1):
        medal = MEDALS.get(i, f"{i}.")
        is_me = "👈" if u['tg_id'] == user.telegram_id else ""
        text += f"{medal} {u['name'][:20]} — <b>{u['weekly_xp']:,} XP</b> {is_me}\n"

    await cb.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:leaderboard")
        ]])
    )
    await cb.answer()


@router.callback_query(F.data == "lb:streak")
async def lb_streak(cb: CallbackQuery, user, **kw):
    top = await sync_to_async(_get_top_streak)(20)
    text = "🔥 <b>Streak reyting</b>\n\n"
    for i, u in enumerate(top, 1):
        medal = MEDALS.get(i, f"{i}.")
        is_me = "👈" if u['tg_id'] == user.telegram_id else ""
        text += f"{medal} {u['name'][:20]} — <b>{u['streak']} kun</b> {is_me}\n"

    await cb.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:leaderboard")
        ]])
    )
    await cb.answer()


def _get_top_xp(limit):
    from apps.users.models import User
    users = User.objects.filter(is_active=True).order_by('-xp_points')[:limit]
    return [{'tg_id': u.telegram_id, 'name': u.full_name,
             'xp': u.xp_points, 'is_premium': u.is_premium} for u in users]


def _get_top_weekly(limit):
    from apps.users.models import User
    from datetime import date, timedelta
    week_ago = date.today() - timedelta(days=7)
    try:
        users = User.objects.filter(
            is_active=True,
            last_active_date__gte=week_ago
        ).order_by('-weekly_xp')[:limit]
        return [{'tg_id': u.telegram_id, 'name': u.full_name,
                 'weekly_xp': getattr(u, 'weekly_xp', 0) or 0} for u in users]
    except Exception:
        return []


def _get_top_streak(limit):
    from apps.users.models import User
    try:
        users = User.objects.filter(
            is_active=True, streak_days__gt=0
        ).order_by('-streak_days')[:limit]
        return [{'tg_id': u.telegram_id, 'name': u.full_name,
                 'streak': u.streak_days or 0} for u in users]
    except Exception:
        return []


def _get_my_rank(user, by='xp'):
    from apps.users.models import User
    if by == 'xp':
        return User.objects.filter(xp_points__gt=user.xp_points).count() + 1
    return 0