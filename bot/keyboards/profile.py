"""Profile keyboards."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def profile_keyboard(lang: str = 'uz') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Tahrirlash", callback_data="profile:edit"),
            InlineKeyboardButton(text="📊 Statistika", callback_data="profile:stats"),
        ],
        [
            InlineKeyboardButton(text="🏆 Sertifikatlar", callback_data="profile:certs"),
            InlineKeyboardButton(text="📚 Tarix", callback_data="profile:history"),
        ],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:main")],
    ])


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang:uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
        ],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:settings")],
    ])


def premium_keyboard(plans, lang: str = 'uz') -> InlineKeyboardMarkup:
    buttons = []
    for plan in plans:
        buttons.append([InlineKeyboardButton(
            text=f"💎 {plan.name} - ${plan.price_usd}",
            callback_data=f"pay:plan:{plan.id}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def payment_method_keyboard(plan_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Click", callback_data=f"pay:click:{plan_id}"),
            InlineKeyboardButton(text="💳 Payme", callback_data=f"pay:payme:{plan_id}"),
        ],
        [InlineKeyboardButton(text="💳 Stripe", callback_data=f"pay:stripe:{plan_id}")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:premium")],
    ])
