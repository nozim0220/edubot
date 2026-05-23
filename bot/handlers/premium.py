"""Premium tizimi — 29,900 so'm/oy."""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async

router = Router()
logger = logging.getLogger('bot')

PREMIUM_PRICE    = 29900   # so'm/oy
PREMIUM_FEATURES = [
    ("♾️", "Cheksiz AI suhbat",              "Kunlik limit yo'q"),
    ("🏫", "Barcha universitetlar to'liq",    "Qabul foizi, narx, stipendiya batafsil"),
    ("🎯", "Shaxsiy o'qish rejasi",           "AI sizga mos kunlik reja tuzadi"),
    ("📈", "Batafsil statistika",             "Grafik, tahlil, kuchli/zaif tomonlar"),
    ("🏆", "Premium sertifikat",              "Tasdiqlangan sertifikat"),
    ("⚡", "Tezkor javob",                    "Navbatsiz xizmat"),
]


# ── PREMIUM MENYU ────────────────────────────────────
@router.callback_query(F.data == "menu:premium")
async def premium_menu(cb: CallbackQuery, user, **kw):
    is_premium = getattr(user, 'is_premium', False)

    if is_premium:
        # Premium bor
        from datetime import datetime
        exp = getattr(user, 'premium_until', None)
        exp_str = exp.strftime('%d.%m.%Y') if exp else "Cheksiz"

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📈 Statistikam",    callback_data="menu:stats")],
            [InlineKeyboardButton(text="🎯 O'qish rejam",   callback_data="menu:study_plan")],
            [InlineKeyboardButton(text="🏠 Bosh menyu",     callback_data="menu:main")],
        ])
        await cb.message.edit_text(
            f"💎 <b>Siz Premium foydalanuvchisiz!</b>\n\n"
            f"📅 Muddat: <b>{exp_str}</b>\n\n"
            f"Sizga mavjud imkoniyatlar:\n"
            + "\n".join(f"{e} {n}" for e,n,_ in PREMIUM_FEATURES),
            reply_markup=kb
        )
    else:
        # Premium yo'q — sotib olish
        features_text = "\n".join(
            f"{e} <b>{n}</b> — <i>{d}</i>"
            for e, n, d in PREMIUM_FEATURES
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f"💳 {PREMIUM_PRICE:,} so'm/oy — Sotib olish",
                callback_data="premium:buy"
            )],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:main")],
        ])
        await cb.message.edit_text(
            f"💎 <b>ABT Premium</b>\n\n"
            f"Narx: <b>{PREMIUM_PRICE:,} so'm / oy</b>\n\n"
            f"Nima olasiz:\n\n"
            f"{features_text}\n\n"
            f"✅ To'lovdan so'ng darhol faollashadi!",
            reply_markup=kb
        )
    await cb.answer()


async def premium_menu_msg(msg: Message, user, **kw):
    """Xabar orqali premium menyu."""
    is_premium = getattr(user, 'is_premium', False)
    features_text = "\n".join(
        f"{e} <b>{n}</b>" for e, n, _ in PREMIUM_FEATURES
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💳 Sotib olish — 29,900 so'm/oy" if not is_premium else "✅ Premium faol",
            callback_data="premium:buy" if not is_premium else "menu:premium"
        )],
    ])
    status = "✅ <b>Premium faol!</b>" if is_premium else "❌ Premium yo'q"
    await msg.answer(
        f"💎 <b>ABT Premium</b>\n\n"
        f"Holat: {status}\n\n"
        f"{features_text}",
        reply_markup=kb
    )


# ── SOTIB OLISH ───────────────────────────────────────
@router.callback_query(F.data == "premium:buy")
async def premium_buy(cb: CallbackQuery, user, **kw):
    from apps.payments.models import Payment
    import uuid

    order_id = str(uuid.uuid4())[:8].upper()

    # Click to'lov URL
    click_url = (
        f"https://my.click.uz/services/pay?"
        f"service_id=12345&"
        f"merchant_id=12345&"
        f"amount={PREMIUM_PRICE}&"
        f"transaction_param={user.pk}_{order_id}&"
        f"return_url=https://t.me/ABTyordamchi0_bot"
    )

    # Payme URL
    import base64, json
    payme_data = base64.b64encode(
        json.dumps({"m": "67a...", "ac": {"order_id": f"{user.pk}_{order_id}"}, "a": PREMIUM_PRICE * 100}).encode()
    ).decode()
    payme_url = f"https://checkout.paycom.uz/{payme_data}"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Click orqali to'lash",  url=click_url)],
        [InlineKeyboardButton(text="💳 Payme orqali to'lash",  url=payme_url)],
        [InlineKeyboardButton(text="💬 Muammo bo'lsa — @ABTyordamchi1", url="https://t.me/ABTyordamchi1")],
        [InlineKeyboardButton(text="🔙 Orqaga",                callback_data="menu:premium")],
    ])
    await cb.message.edit_text(
        f"💳 <b>Premium to'lov</b>\n\n"
        f"💰 Summa: <b>{PREMIUM_PRICE:,} so'm</b>\n"
        f"📦 Muddati: <b>1 oy</b>\n"
        f"🔐 Order ID: <code>{order_id}</code>\n\n"
        f"To'lov usulini tanlang:\n\n"
        f"⚠️ To'lovdan keyin <b>1-5 daqiqa</b> ichida faollashadi.\n"
        f"Muammo bo'lsa: @ABTyordamchi1",
        reply_markup=kb
    )
    await cb.answer()


# ── ADMIN TOMONIDAN PREMIUM BERISH ────────────────────
@router.callback_query(F.data.startswith("adm:premium:"))
async def admin_give_premium(cb: CallbackQuery, user, **kw):
    """Admin foydalanuvchiga premium beradi."""
    if not getattr(user, 'is_staff', False):
        await cb.answer("❌", show_alert=True); return

    from apps.users.models import User
    from datetime import datetime, timedelta

    parts = cb.data.split(":")
    target_id = int(parts[2])
    days      = int(parts[3]) if len(parts) > 3 else 30

    try:
        target = await sync_to_async(User.objects.get)(pk=target_id)
        target.is_premium = True
        target.premium_until = datetime.now() + timedelta(days=days)
        await sync_to_async(target.save)()
        await cb.answer(f"✅ {target.full_name} ga {days} kunlik premium berildi!", show_alert=True)
    except User.DoesNotExist:
        await cb.answer("❌ Topilmadi", show_alert=True)