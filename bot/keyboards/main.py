"""Asosiy klaviaturalar."""
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)


def main_menu_keyboard(lang: str = "uz", is_admin: bool = False) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🏫 Universitetlar")],
        [KeyboardButton(text="🤖 AI Yordamchi"),  KeyboardButton(text="👤 Profil")],
        [KeyboardButton(text="💎 Premium"),        KeyboardButton(text="🎮 O'yinlar")],
        [KeyboardButton(text="🏆 Reyting"),        KeyboardButton(text="🔥 Kunlik vazifa")],
        [KeyboardButton(text="✍️ Writing")],
        [KeyboardButton(text="⏰ Imtihon sana"), KeyboardButton(text="📊 Xato tahlili")],
        [KeyboardButton(text="⚙️ Sozlamalar"),   KeyboardButton(text="🆘 Yordam")],
        [KeyboardButton(text="👥 Referal")],
    ]
    if is_admin:
        buttons.append([KeyboardButton(text="🔐 Admin Panel")])
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        persistent=True,
        input_field_placeholder="Buyruq tanlang...",
    )


def back_keyboard(cb: str = "menu:main") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data=cb)]
    ])


def back_and_main(back_cb: str = "menu:main") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Orqaga",     callback_data=back_cb),
            InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:main"),
        ]
    ])


def inline_main_menu(lang: str = "uz", is_admin: bool = False) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🏫 Universitetlar", callback_data="menu:universities"),
        ],
        [
            InlineKeyboardButton(text="🤖 AI Yordamchi",  callback_data="menu:ai"),
            InlineKeyboardButton(text="👤 Profil",         callback_data="menu:profile"),
        ],
        [
            InlineKeyboardButton(text="💎 Premium",        callback_data="menu:premium"),
            InlineKeyboardButton(text="🎮 O'yinlar",       callback_data="menu:games"),
        ],
        [
            InlineKeyboardButton(text="🏆 Reyting",        callback_data="menu:leaderboard"),
            InlineKeyboardButton(text="🔥 Kunlik vazifa",  callback_data="menu:daily"),
        ],
        [
            InlineKeyboardButton(text="⚙️ Sozlamalar",     callback_data="menu:settings"),
            InlineKeyboardButton(text="👥 Referal",         callback_data="menu:referral"),
        ],
    ]
    if is_admin:
        buttons.append([InlineKeyboardButton(text="🔐 Admin Panel", callback_data="adm:panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)