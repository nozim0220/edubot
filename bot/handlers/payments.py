"""To'lov handler."""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async

from bot.keyboards.main import back_keyboard

router = Router()
logger = logging.getLogger('bot')


@router.callback_query(F.data == "menu:premium")
async def premium_menu(callback: CallbackQuery, user, **kwargs):
    from apps.payments.models import PremiumPlan
    plans = await sync_to_async(list)(PremiumPlan.objects.filter(is_active=True))
    features = [
        "🤖 Cheksiz AI so'rovlar",
        "📝 Mock imtihonlar",
        "📊 Kengaytirilgan statistika",
        "🏛 VIP universitet tavsiyalari",
        "📅 Shaxsiy o'qish rejasi",
    ]
    feat_text = "\n".join(f"✅ {f}" for f in features)
    status = "💎 Premium FAOL ✅" if user.is_premium_active else "🔓 Oddiy hisob"

    buttons = []
    for plan in plans:
        buttons.append([InlineKeyboardButton(
            text=f"💎 {plan.name} — ${plan.price_usd} / {int(plan.price_uzs):,} so'm",
            callback_data=f"pay:plan:{plan.pk}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:main")])

    await callback.message.edit_text(
        f"💎 <b>Premium obuna</b>\n\n{feat_text}\n\n{status}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay:plan:"))
async def select_plan(callback: CallbackQuery, **kwargs):
    plan_id = int(callback.data.split(":")[2])
    from apps.payments.models import PremiumPlan
    plan = await sync_to_async(PremiumPlan.objects.get)(pk=plan_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Click",  callback_data=f"pay:click:{plan_id}")],
        [InlineKeyboardButton(text="💳 Payme",  callback_data=f"pay:payme:{plan_id}")],
        [InlineKeyboardButton(text="💳 Stripe (Visa/MC)", callback_data=f"pay:stripe:{plan_id}")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:premium")],
    ])
    await callback.message.edit_text(
        f"💎 <b>{plan.name}</b>\n\n"
        f"💰 ${plan.price_usd} / {int(plan.price_uzs):,} so'm\n"
        f"📅 {plan.duration_days or '∞'} kun\n\n"
        f"To'lov usulini tanlang:",
        reply_markup=kb,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay:click:"))
async def pay_click(callback: CallbackQuery, user, **kwargs):
    plan_id = int(callback.data.split(":")[2])
    from apps.payments.models import PremiumPlan
    from apps.payments.services import ClickService
    plan = await sync_to_async(PremiumPlan.objects.get)(pk=plan_id)
    result = await sync_to_async(ClickService.prepare_url)(user, plan)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Click orqali to'lash", url=result['payment_url'])],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:premium")],
    ])
    await callback.message.edit_text(
        f"💳 <b>Click orqali to'lash</b>\n\nOrder: <code>{result['order_id']}</code>",
        reply_markup=kb,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay:payme:"))
async def pay_payme(callback: CallbackQuery, user, **kwargs):
    plan_id = int(callback.data.split(":")[2])
    from apps.payments.models import PremiumPlan
    from apps.payments.services import PaymeService
    plan = await sync_to_async(PremiumPlan.objects.get)(pk=plan_id)
    result = await sync_to_async(PaymeService.prepare_url)(user, plan)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Payme orqali to'lash", url=result['payment_url'])],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:premium")],
    ])
    await callback.message.edit_text(
        f"💳 <b>Payme orqali to'lash</b>\n\nOrder: <code>{result['order_id']}</code>",
        reply_markup=kb,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay:stripe:"))
async def pay_stripe(callback: CallbackQuery, user, **kwargs):
    plan_id = int(callback.data.split(":")[2])
    from apps.payments.models import PremiumPlan
    plan = await sync_to_async(PremiumPlan.objects.get)(pk=plan_id)
    try:
        from apps.payments.services import StripeService
        result = await sync_to_async(StripeService.create_payment_intent)(user, plan)
        await callback.message.edit_text(
            f"💳 <b>Stripe (Visa/MC)</b>\n\n"
            f"Order: <code>{result['order_id']}</code>\n\n"
            f"To'lov sahifasi: https://yourdomain.com/pay/{result['order_id']}",
            reply_markup=back_keyboard("menu:premium"),
        )
    except Exception:
        await callback.answer("Stripe hozircha mavjud emas.", show_alert=True)
    await callback.answer()
