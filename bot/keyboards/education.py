"""Education keyboards."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List


def subjects_keyboard(subjects, lang: str = 'uz') -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for i, subject in enumerate(subjects):
        name = getattr(subject, f'name_{lang}', subject.name_en)
        row.append(InlineKeyboardButton(
            text=f"{subject.emoji} {name}",
            callback_data=f"subject:{subject.id}"
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def subject_actions_keyboard(subject_id: int, lang: str = 'uz') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎯 Test ishlash", callback_data=f"edu:quiz:{subject_id}"),
            InlineKeyboardButton(text="📝 Mock Exam", callback_data=f"edu:mock:{subject_id}"),
        ],
        [
            InlineKeyboardButton(text="🎲 Random", callback_data=f"edu:random:{subject_id}"),
            InlineKeyboardButton(text="📊 Natijalarim", callback_data=f"edu:progress:{subject_id}"),
        ],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:education")],
    ])


def question_keyboard(options: dict, session_id: int, question_id: int) -> InlineKeyboardMarkup:
    buttons = []
    labels = {'A': options.get('a'), 'B': options.get('b'), 'C': options.get('c'), 'D': options.get('d')}
    row = []
    for letter, text in labels.items():
        if text:
            row.append(InlineKeyboardButton(
                text=f"{letter}",
                callback_data=f"ans:{session_id}:{question_id}:{letter}"
            ))
    buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def test_result_keyboard(subject_id: int, lang: str = 'uz') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Qayta urinish", callback_data=f"edu:quiz:{subject_id}"),
            InlineKeyboardButton(text="📚 Fanlar", callback_data="menu:education"),
        ],
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:main")],
    ])
