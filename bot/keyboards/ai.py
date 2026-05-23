"""AI assistant keyboards."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def ai_menu_keyboard(lang: str = 'uz') -> InlineKeyboardMarkup:
    items = [
        ("📝 Uy ishi yordam", "ai:homework"),
        ("🧮 Matematika", "ai:math"),
        ("📖 Mavzuni tushuntir", "ai:explain"),
        ("✍️ Grammatika tekshir", "ai:grammar"),
        ("📄 Insho yozish", "ai:essay"),
        ("🎯 Karyera maslahat", "ai:career"),
        ("📅 O'qish rejasi", "ai:study_plan"),
        ("💬 Erkin suhbat", "ai:general"),
    ]
    buttons = []
    row = []
    for text, cb in items:
        row.append(InlineKeyboardButton(text=text, callback_data=cb))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([
        InlineKeyboardButton(text="📋 Tarix", callback_data="ai:history"),
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:main"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def ai_stop_keyboard(lang: str = 'uz') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⏹ Tugatish", callback_data="ai:stop"),
            InlineKeyboardButton(text="💾 Saqlash", callback_data="ai:save_chat"),
        ],
        [InlineKeyboardButton(text="🔙 AI Menyu", callback_data="menu:ai")],
    ])
