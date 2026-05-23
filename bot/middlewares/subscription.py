"""Majburiy kanal obunasi middleware."""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update

# Kanal sozlamalari — o'zingizning kanalingizni qo'ying
REQUIRED_CHANNELS = [
    {
        "id":   "@ABTyordamchi1",
        "name": "ABTyordamchi",
        "url":  "https://t.me/ABTyordamchi1",
    }
]


async def check_all_channels(bot, user_id: int, channels=None) -> bool:
    """Barcha kanallarga obuna bo'lganmi."""
    chs = channels or REQUIRED_CHANNELS
    if not chs:
        return True
    for ch in chs:
        try:
            member = await bot.get_chat_member(chat_id=ch["id"], user_id=user_id)
            if member.status in ('left', 'kicked'):
                return False
        except Exception:
            pass
    return True


class SubscriptionMiddleware(BaseMiddleware):
    SKIP_CALLBACKS = {'check_sub', 'menu:main'}
    SKIP_COMMANDS  = {'/start', '/help'}

    async def __call__(
        self,
        handler: Callable,
        event,
        data: Dict[str, Any]
    ) -> Any:
        if not REQUIRED_CHANNELS:
            return await handler(event, data)

        bot = data.get('bot') or getattr(event, 'bot', None)
        if not bot:
            return await handler(event, data)

        if isinstance(event, CallbackQuery):
            if event.data in self.SKIP_CALLBACKS:
                return await handler(event, data)
            user_id = event.from_user.id
        elif isinstance(event, Message):
            if event.text and event.text.split()[0] in self.SKIP_COMMANDS:
                return await handler(event, data)
            user_id = event.from_user.id if event.from_user else None
        else:
            return await handler(event, data)

        if not user_id:
            return await handler(event, data)

        is_sub = await check_all_channels(bot, user_id, REQUIRED_CHANNELS)
        if not is_sub:
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            ch = REQUIRED_CHANNELS[0]
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"📢 {ch['name']} ga obuna", url=ch['url'])],
                [InlineKeyboardButton(text="✅ Obuna bo'ldim", callback_data="check_sub")],
            ])
            text = (
                f"⛔ <b>Kanalga obuna bo'ling!</b>\n\n"
                f"📢 <b>{ch['name']}</b>\n\n"
                f"Obuna bo'lgach <b>✅ Obuna bo'ldim</b> tugmasini bosing."
            )
            if isinstance(event, CallbackQuery):
                try:
                    await event.message.edit_text(text, reply_markup=kb)
                except Exception:
                    await event.message.answer(text, reply_markup=kb)
                await event.answer()
            else:
                await event.answer(text, reply_markup=kb)
            return

        return await handler(event, data)