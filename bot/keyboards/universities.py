"""University keyboards."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def university_search_keyboard(lang: str = 'uz') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 Qidirish", callback_data="uni:search"),
            InlineKeyboardButton(text="⭐ Tavsiyalar", callback_data="uni:recommend"),
        ],
        [
            InlineKeyboardButton(text="🌍 Mamlakatlar bo'yicha", callback_data="uni:by_country"),
            InlineKeyboardButton(text="❤️ Saqlangan", callback_data="uni:saved"),
        ],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:main")],
    ])


def country_filter_keyboard() -> InlineKeyboardMarkup:
    countries = [
        ("🇺🇿 O'zbekiston", "UZ"), ("🇺🇸 USA", "US"),
        ("🇬🇧 UK", "GB"), ("🇩🇪 Germany", "DE"),
        ("🇷🇺 Russia", "RU"), ("🇰🇷 S.Korea", "KR"),
        ("🇹🇷 Turkey", "TR"), ("🇨🇳 China", "CN"),
    ]
    buttons = []
    row = []
    for name, code in countries:
        row.append(InlineKeyboardButton(text=name, callback_data=f"uni:country:{code}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:universities")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def university_detail_keyboard(uni_id: int, is_saved: bool = False) -> InlineKeyboardMarkup:
    save_text = "💔 Saqlangan" if is_saved else "❤️ Saqlash"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=save_text, callback_data=f"uni:toggle_save:{uni_id}"),
            InlineKeyboardButton(text="🌐 Sayt", callback_data=f"uni:website:{uni_id}"),
        ],
        [
            InlineKeyboardButton(text="🎓 Fakultetlar", callback_data=f"uni:faculties:{uni_id}"),
            InlineKeyboardButton(text="🤖 AI Tavsiya", callback_data=f"uni:ai_advice:{uni_id}"),
        ],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:universities")],
    ])
