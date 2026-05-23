"""Sozlamalar — til, bildirishnomalar."""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from bot.middlewares.auth import invalidate_user_cache

router = Router()
logger = logging.getLogger('bot')

LANGS = {
    'uz': ("🇺🇿", "O'zbek tili"),
    'ru': ("🇷🇺", "Русский язык"),
    'en': ("🇬🇧", "English"),
}


@router.message(F.text == "⚙️ Sozlamalar")
async def settings_msg(msg: Message, user, **kw):
    await _show_settings(msg, user)


@router.callback_query(F.data == "menu:settings")
async def settings_cb(cb: CallbackQuery, user, **kw):
    await _show_settings(cb.message, user, edit=True)
    await cb.answer()


async def _show_settings(msg, user, edit=False):
    current_lang = getattr(user, 'language', 'uz')
    flag, lang_name = LANGS.get(current_lang, ("🇺🇿", "O'zbek tili"))

    kb = InlineKeyboardMarkup(inline_keyboard=[
        # Til tanlash
        [InlineKeyboardButton(
            text=f"{'✅ ' if current_lang=='uz' else ''}🇺🇿 O'zbek tili",
            callback_data="lang:uz"
        )],
        [InlineKeyboardButton(
            text=f"{'✅ ' if current_lang=='ru' else ''}🇷🇺 Русский",
            callback_data="lang:ru"
        )],
        [InlineKeyboardButton(
            text=f"{'✅ ' if current_lang=='en' else ''}🇬🇧 English",
            callback_data="lang:en"
        )],
        [InlineKeyboardButton(text="🔙 Bosh menyu", callback_data="menu:main")],
    ])

    text = (
        f"⚙️ <b>Sozlamalar</b>\n\n"
        f"🌐 Hozirgi til: <b>{flag} {lang_name}</b>\n\n"
        f"Tilni tanlang:"
    )

    if edit:
        try:
            await msg.edit_text(text, reply_markup=kb)
        except Exception:
            await msg.answer(text, reply_markup=kb)
    else:
        await msg.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("lang:"))
async def change_language(cb: CallbackQuery, user, **kw):
    lang = cb.data.split(":")[1]

    if lang not in LANGS:
        await cb.answer("❌ Noto'g'ri til", show_alert=True)
        return

    # DB ga saqlash
    try:
        await sync_to_async(_save_language)(user, lang)
        # Cache tozalash — keyingi xabarda yangi til ishlaydi
        invalidate_user_cache(user.telegram_id)
    except Exception as e:
        logger.error(f"Til saqlash xatosi: {e}")
        await cb.answer("❌ Xatolik!", show_alert=True)
        return

    flag, lang_name = LANGS[lang]

    # Tilga qarab xabar
    messages = {
        'uz': f"✅ Til o'zgartirildi: {flag} O'zbek tili",
        'ru': f"✅ Язык изменён: {flag} Русский",
        'en': f"✅ Language changed: {flag} English",
    }

    await cb.answer(messages[lang], show_alert=True)

    # Sozlamalar menyusini yangilash
    current_lang = lang
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{'✅ ' if current_lang=='uz' else ''}🇺🇿 O'zbek tili",
            callback_data="lang:uz"
        )],
        [InlineKeyboardButton(
            text=f"{'✅ ' if current_lang=='ru' else ''}🇷🇺 Русский",
            callback_data="lang:ru"
        )],
        [InlineKeyboardButton(
            text=f"{'✅ ' if current_lang=='en' else ''}🇬🇧 English",
            callback_data="lang:en"
        )],
        [InlineKeyboardButton(text="🔙 Bosh menyu", callback_data="menu:main")],
    ])

    f2, n2 = LANGS[lang]
    try:
        await cb.message.edit_text(
            f"⚙️ <b>Sozlamalar</b>\n\n"
            f"🌐 Hozirgi til: <b>{f2} {n2}</b>\n\n"
            f"Tilni tanlang:",
            reply_markup=kb
        )
    except Exception:
        pass


def _save_language(user, lang: str):
    """Sinxron DB saqlash."""
    from apps.users.models import User
    User.objects.filter(pk=user.pk).update(language=lang)