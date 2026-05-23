"""
Universitetlar — bepul 5 ta, premium 20,000 so'm qo'shimcha 5 ta.
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async

router = Router()
logger = logging.getLogger('bot')

FREE_UNI_LIMIT    = 5   # Bepul ko'rish
PREMIUM_UNI_PRICE = 20000  # So'm — qo'shimcha 5 ta
PREMIUM_UNI_COUNT = 5   # To'lovdan keyin qo'shimcha


@router.callback_query(F.data == "uni:list")
async def uni_list(cb: CallbackQuery, user, **kw):
    """Universitetlar ro'yxati — 5 ta bepul."""
    from apps.universities.models import University

    unis = await sync_to_async(
        lambda: list(University.objects.filter(is_active=True).order_by('world_ranking', 'national_ranking')[:FREE_UNI_LIMIT])
    )()

    flags = {'UZ':'🇺🇿','US':'🇺🇸','GB':'🇬🇧','DE':'🇩🇪',
             'KR':'🇰🇷','TR':'🇹🇷','CN':'🇨🇳','JP':'🇯🇵'}

    text = "🏫 <b>Universitetlar</b>\n\n"
    btns = []
    for u in unis:
        flag = flags.get(u.country, '🌍')
        rank = f"#{u.world_ranking}" if u.world_ranking else ""
        text += f"{flag} <b>{u.name}</b> {rank}\n"
        btns.append([InlineKeyboardButton(
            text=f"{flag} {u.name[:40]}",
            callback_data=f"uni:detail:{u.pk}"
        )])

    # Qo'shimcha 5 ta uchun to'lov
    is_premium = getattr(user, 'is_premium', False)
    has_uni_access = await _check_uni_access(user)

    if not has_uni_access and not is_premium:
        text += f"\n🔒 <b>+5 ta universitet</b> — {PREMIUM_UNI_PRICE:,} so'm\n"
        btns.append([InlineKeyboardButton(
            text=f"🔓 +5 ta ko'rish — {PREMIUM_UNI_PRICE:,} so'm",
            callback_data="uni:buy_more"
        )])
    elif has_uni_access or is_premium:
        # Premium yoki to'langan — 10 ta ko'rsatish
        extra_unis = await sync_to_async(
            lambda: list(University.objects.filter(is_active=True)
                        .order_by('world_ranking')[FREE_UNI_LIMIT:FREE_UNI_LIMIT+PREMIUM_UNI_COUNT])
        )()
        for u in extra_unis:
            flag = flags.get(u.country, '🌍')
            btns.append([InlineKeyboardButton(
                text=f"{flag} {u.name[:40]} ⭐",
                callback_data=f"uni:detail:{u.pk}"
            )])

    btns.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:universities")])

    await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=btns))
    await cb.answer()


async def _check_uni_access(user) -> bool:
    """Foydalanuvchi to'lagan yoki premium."""
    if getattr(user, 'is_premium', False):
        return True
    try:
        from apps.payments.models import Payment
        paid = await sync_to_async(
            Payment.objects.filter(
                user=user, purpose='uni_access', status='paid'
            ).exists
        )()
        return paid
    except Exception:
        return False


@router.callback_query(F.data == "uni:buy_more")
async def uni_buy_more(cb: CallbackQuery, user, **kw):
    """Qo'shimcha 5 ta universitet uchun to'lov."""
    import uuid
    order_id = str(uuid.uuid4())[:8].upper()

    click_url = (
        f"https://my.click.uz/services/pay?"
        f"service_id=12345&merchant_id=12345&"
        f"amount={PREMIUM_UNI_PRICE}&"
        f"transaction_param=uni_{user.pk}_{order_id}&"
        f"return_url=https://t.me/ABTyordamchi0_bot"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Click orqali to'lash", url=click_url)],
        [InlineKeyboardButton(text="💎 Premium ol (hammasi ochiq)", callback_data="premium:buy")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="uni:list")],
    ])
    await cb.message.edit_text(
        f"🏫 <b>Qo'shimcha 5 ta universitet</b>\n\n"
        f"💰 Narx: <b>{PREMIUM_UNI_PRICE:,} so'm</b> (bir martalik)\n\n"
        f"Yoki <b>Premium</b> oling — barcha universitetlar ochiq!\n"
        f"Premium: <b>29,900 so'm/oy</b>",
        reply_markup=kb
    )
    await cb.answer()