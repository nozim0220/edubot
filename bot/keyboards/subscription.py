"""Subscription check keyboard."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List


def subscription_keyboard(channels: List[str], lang: str = 'uz') -> InlineKeyboardMarkup:
    buttons = []
    for i, channel in enumerate(channels, 1):
        name = channel.lstrip('@')
        buttons.append([InlineKeyboardButton(text=f"📢 {name}", url=f"https://t.me/{name.lstrip('@')}")])
    
    check_text = {'uz': "✅ Tekshirish", 'ru': "✅ Проверить", 'en': "✅ Check"}.get(lang, "✅ Tekshirish")
    buttons.append([InlineKeyboardButton(text=check_text, callback_data="check_subscription")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
