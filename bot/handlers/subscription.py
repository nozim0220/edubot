"""Majburiy kanal obunasi."""
import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

router = Router()
logger = logging.getLogger('bot')

# ── KANAL SOZLAMALARI ─────────────────────────────────
# O'zingizning kanalingizni shu yerga qo'ying
REQUIRED_CHANNEL = {
    "id":       "@abt_prep",          # Kanal username
    "name":     "ABT Prep",           # Ko'rsatiladigan nom
    "url":      "https://t.me/abt_prep",  # Havola
}


async def check_subscription(bot: Bot, user_id: int) -> bool:
    """Foydalanuvchi kanalga obuna bo'lganmi?"""
    try:
        member = await bot.get_chat_member(
            chat_id=REQUIRED_CHANNEL["id"],
            user_id=user_id
        )
        return member.status not in ('left', 'kicked', 'restricted')
    except Exception as e:
        logger.debug(f"Subscription check: {e}")
        return True  # Xato bo'lsa ruxsat berish


async def require_subscription(msg_or_cb, bot: Bot, user_id: int) -> bool:
    """
    Obuna tekshiradi. Obuna bo'lmasa xabar yuboradi.
    Returns: True = davom etish mumkin, False = obuna kerak
    """
    if await check_subscription(bot, user_id):
        return True

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"📢 {REQUIRED_CHANNEL['name']} ga obuna bo'lish",
            url=REQUIRED_CHANNEL["url"]
        )],
        [InlineKeyboardButton(
            text="✅ Obuna bo'ldim",
            callback_data="check_sub"
        )],
    ])

    text = (
        f"⛔ <b>Botdan foydalanish uchun kanalga obuna bo'ling!</b>\n\n"
        f"📢 Kanal: <b>{REQUIRED_CHANNEL['name']}</b>\n\n"
        f"Obuna bo'lgandan keyin <b>\"✅ Obuna bo'ldim\"</b> tugmasini bosing."
    )

    if isinstance(msg_or_cb, CallbackQuery):
        try:
            await msg_or_cb.message.edit_text(text, reply_markup=kb)
        except Exception:
            await msg_or_cb.message.answer(text, reply_markup=kb)
        await msg_or_cb.answer()
    else:
        await msg_or_cb.answer(text, reply_markup=kb)

    return False


# ── OBUNA TEKSHIRISH TUGMASI ──────────────────────────
@router.callback_query(F.data == "check_sub")
async def check_sub_callback(cb: CallbackQuery, **kw):
    bot = cb.bot
    is_subscribed = await check_subscription(bot, cb.from_user.id)

    if is_subscribed:
        await cb.answer("✅ Rahmat! Endi botdan foydalanishingiz mumkin!", show_alert=True)
        # Bosh menyuga qaytarish
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:main")]
        ])
        await cb.message.edit_text(
            "✅ <b>Obuna tasdiqlandi!</b>\n\nBotdan to'liq foydalanishingiz mumkin.",
            reply_markup=kb
        )
    else:
        await cb.answer(
            f"❌ Hali obuna bo'lmadingiz!\n{REQUIRED_CHANNEL['url']} ga o'ting.",
            show_alert=True
        )