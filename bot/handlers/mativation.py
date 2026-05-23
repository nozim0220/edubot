"""Flashcard — so'zlarni takrorlash (spaced repetition)."""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async

router = Router()
logger = logging.getLogger('bot')

FLASHCARDS = [
    {"word": "Perseverance", "meaning": "Qat'iyat", "example": "Perseverance leads to success."},
    {"word": "Eloquent",     "meaning": "Notiq",    "example": "An eloquent speaker."},
    {"word": "Meticulous",   "meaning": "Puxta",    "example": "Meticulous attention to detail."},
    {"word": "Ambiguous",    "meaning": "Noaniq",   "example": "An ambiguous answer."},
    {"word": "Inevitable",   "meaning": "Muqarrar", "example": "Change is inevitable."},
    {"word": "Pragmatic",    "meaning": "Amaliy",   "example": "A pragmatic solution."},
    {"word": "Resilient",    "meaning": "Chidamli", "example": "A resilient person."},
    {"word": "Diligent",     "meaning": "Mehnatsevar", "example": "A diligent student."},
    {"word": "Versatile",    "meaning": "Ko'p qirrali", "example": "A versatile athlete."},
    {"word": "Candid",       "meaning": "Samimiy",  "example": "A candid opinion."},
    {"word": "Profound",     "meaning": "Chuqur",   "example": "A profound impact."},
    {"word": "Tenacious",    "meaning": "Qaysarona","example": "A tenacious worker."},
    {"word": "Benevolent",   "meaning": "Xayrli",   "example": "A benevolent leader."},
    {"word": "Innovative",   "meaning": "Innovatsion","example": "An innovative idea."},
    {"word": "Integrity",    "meaning": "Halollik", "example": "A man of integrity."},
    {"word": "Ambitious",    "meaning": "Shijoatli","example": "An ambitious goal."},
    {"word": "Empathy",      "meaning": "Hamdardlik","example": "Show empathy to others."},
    {"word": "Consistent",   "meaning": "Izchil",   "example": "Be consistent in efforts."},
    {"word": "Resourceful",  "meaning": "Topqir",   "example": "A resourceful person."},
    {"word": "Courageous",   "meaning": "Jasur",    "example": "A courageous decision."},
]


@router.callback_query(F.data == "menu:flashcard")
async def flashcard_menu(cb: CallbackQuery, user, **kw):
    stats = await sync_to_async(_get_flashcard_stats)(user)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ O'rganishni boshlash", callback_data="fc:start:0")],
        [InlineKeyboardButton(text="🔄 Takrorlash (zaif so'zlar)", callback_data="fc:review")],
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:main")],
    ])
    known = stats.get('known', 0)
    total = len(FLASHCARDS)
    await cb.message.edit_text(
        f"🃏 <b>Flashcard — So'z o'rganish</b>\n\n"
        f"📊 O'rganilgan: <b>{known}/{total}</b>\n"
        f"🔄 Takrorlash kerak: <b>{stats.get('review', 0)}</b>\n\n"
        f"Har kuni 5-10 ta so'z o'rganing!",
        reply_markup=kb
    )
    await cb.answer()


@router.callback_query(F.data.startswith("fc:start:"))
async def flashcard_show(cb: CallbackQuery, user, **kw):
    idx = int(cb.data.split(":")[2])
    if idx >= len(FLASHCARDS):
        await cb.message.edit_text(
            "🎉 <b>Barcha so'zlarni ko'rdingiz!</b>\n\n"
            "Endi takrorlash vaqti.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🔄 Takrorlash", callback_data="fc:review"),
                InlineKeyboardButton(text="🏠 Menyu", callback_data="menu:main"),
            ]])
        )
        await cb.answer()
        return

    card = FLASHCARDS[idx]
    await cb.message.edit_text(
        f"🃏 <b>{idx+1}/{len(FLASHCARDS)}</b>\n\n"
        f"🔤 <b>{card['word']}</b>\n\n"
        f"📝 <i>{card['example']}</i>\n\n"
        f"Ma'nosini bilasizmi?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Bilaman", callback_data=f"fc:know:{idx}"),
             InlineKeyboardButton(text="❌ Bilmayman", callback_data=f"fc:dontknow:{idx}")],
            [InlineKeyboardButton(text="⏭ O'tkazish", callback_data=f"fc:start:{idx+1}")],
        ])
    )
    await cb.answer()


@router.callback_query(F.data.startswith("fc:know:"))
async def fc_know(cb: CallbackQuery, user, **kw):
    idx = int(cb.data.split(":")[2])
    card = FLASHCARDS[idx]
    await sync_to_async(_mark_known)(user, card['word'], True)
    await cb.answer("✅ Zo'r!")
    # Keyingi karta
    next_idx = idx + 1
    if next_idx < len(FLASHCARDS):
        cb.data = f"fc:start:{next_idx}"
        await flashcard_show(cb, user)
    else:
        await cb.message.edit_text(
            "🎉 Session tugadi!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🏠 Menyu", callback_data="menu:main")
            ]])
        )


@router.callback_query(F.data.startswith("fc:dontknow:"))
async def fc_dontknow(cb: CallbackQuery, user, **kw):
    idx = int(cb.data.split(":")[2])
    card = FLASHCARDS[idx]
    await sync_to_async(_mark_known)(user, card['word'], False)
    await cb.message.edit_text(
        f"📖 <b>{card['word']}</b>\n\n"
        f"✏️ Ma'nosi: <b>{card['meaning']}</b>\n\n"
        f"💬 <i>{card['example']}</i>\n\n"
        f"Eslab qoling!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="➡️ Davom", callback_data=f"fc:start:{idx+1}")
        ]])
    )
    await cb.answer()


@router.callback_query(F.data == "fc:review")
async def fc_review(cb: CallbackQuery, user, **kw):
    weak = await sync_to_async(_get_weak_words)(user)
    if not weak:
        await cb.answer("Hozircha zaif so'z yo'q!", show_alert=True)
        return
    import random
    card = random.choice(weak)
    idx = next((i for i, c in enumerate(FLASHCARDS) if c['word'] == card), 0)
    cb.data = f"fc:start:{idx}"
    await flashcard_show(cb, user)


def _get_flashcard_stats(user):
    from apps.users.models import User
    try:
        u = User.objects.get(pk=user.pk)
        notes = u.notes or {}
        fc = notes.get('flashcards', {})
        known  = sum(1 for v in fc.values() if v.get('known'))
        review = sum(1 for v in fc.values() if not v.get('known'))
        return {'known': known, 'review': review}
    except Exception:
        return {'known': 0, 'review': 0}


def _mark_known(user, word, known):
    from apps.users.models import User
    try:
        u = User.objects.get(pk=user.pk)
        notes = u.notes or {}
        if 'flashcards' not in notes:
            notes['flashcards'] = {}
        notes['flashcards'][word] = {'known': known}
        u.notes = notes
        u.save(update_fields=['notes'])
    except Exception:
        pass


def _get_weak_words(user):
    from apps.users.models import User
    try:
        u = User.objects.get(pk=user.pk)
        notes = u.notes or {}
        fc = notes.get('flashcards', {})
        return [w for w, v in fc.items() if not v.get('known')]
    except Exception:
        return []