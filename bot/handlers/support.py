"""Support — AI javob beradi, adminlarga xabar yuboradi."""
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async

router = Router()
logger = logging.getLogger('bot')

SUPPORT_USERNAME = "ABTyordamchi1"  # Support kanal/guruh


class SupportSt(StatesGroup):
    waiting_message = State()


# ── SUPPORT MENYU ────────────────────────────────────
@router.message(F.text == "🆘 Yordam")
@router.callback_query(F.data == "menu:support")
async def support_menu(event, user, state: FSMContext, **kw):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 AI ga savol berish",   callback_data="support:ai")],
        [InlineKeyboardButton(text="👨‍💼 Operatorga yozish",    callback_data="support:human")],
        [InlineKeyboardButton(text="📋 Ko'p so'raladigan savollar", callback_data="support:faq")],
        [InlineKeyboardButton(text="🔙 Bosh menyu",           callback_data="menu:main")],
    ])
    msg = event.message if isinstance(event, CallbackQuery) else event
    text = (
        "🆘 <b>ABT Yordam Markazi</b>\n\n"
        "Qanday yordam kerak?\n\n"
        "🤖 <b>AI Yordam</b> — tezkor javob\n"
        "👨‍💼 <b>Operator</b> — murakkab savollar\n"
        "📋 <b>FAQ</b> — tez-tez so'raladigan savollar"
    )
    try:
        await msg.edit_text(text, reply_markup=kb)
    except Exception:
        await msg.answer(text, reply_markup=kb)
    if isinstance(event, CallbackQuery):
        await event.answer()


# ── AI YORDAM ────────────────────────────────────────
@router.callback_query(F.data == "support:ai")
async def support_ai_start(cb: CallbackQuery, state: FSMContext, **kw):
    await state.set_state(SupportSt.waiting_message)
    await state.update_data(support_type='ai')
    await cb.message.edit_text(
        "🤖 <b>AI Yordamchi</b>\n\n"
        "Savolingizni yozing — AI darhol javob beradi!\n\n"
        "Masalan:\n"
        "• IELTS bandim qanday oshiraman?\n"
        "• Qaysi universitetga kirish oson?\n"
        "• Premium nima beradi?\n\n"
        "✍️ Savolingizni yozing:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="❌ Bekor", callback_data="menu:support")
        ]])
    )
    await cb.answer()


# ── OPERATOR ─────────────────────────────────────────
@router.callback_query(F.data == "support:human")
async def support_human(cb: CallbackQuery, state: FSMContext, **kw):
    await state.set_state(SupportSt.waiting_message)
    await state.update_data(support_type='human')
    await cb.message.edit_text(
        "👨‍💼 <b>Operator bilan bog'lanish</b>\n\n"
        "Muammongizni batafsil yozing.\n"
        "Operator 24 soat ichida javob beradi.\n\n"
        "✍️ Xabaringizni yozing:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="❌ Bekor", callback_data="menu:support")
        ]])
    )
    await cb.answer()


# ── FAQ ───────────────────────────────────────────────
@router.callback_query(F.data == "support:faq")
async def support_faq(cb: CallbackQuery, **kw):
    faqs = [
        ("💎 Premium nima?",
         "Premium — cheksiz AI, barcha universitetlar, kirish foizi, shaxsiy reja. 29,900 so'm/oy."),
        ("💳 Qanday to'layman?",
         "Click yoki Payme orqali. Premium tugmasi → to'lov usulini tanlang."),
        ("🏫 Universitetlar qancha?",
         "20+ universitet. Bepul: 5 ta. Premium: hammasi."),
        ("🤖 AI nechta savol?",
         "Bepul: kuniga 10 ta. Premium: cheksiz."),
        ("📊 IELTS/SAT ball qo'shish?",
         "👤 Profil → ✏️ Tahrirlash → ball kiriting."),
    ]
    text = "📋 <b>Ko'p so'raladigan savollar:</b>\n\n"
    for q, a in faqs:
        text += f"<b>{q}</b>\n{a}\n\n"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Boshqa savol — AI ga", callback_data="support:ai")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:support")],
    ])
    await cb.message.edit_text(text, reply_markup=kb)
    await cb.answer()


# ── XABAR QABUL QILISH ───────────────────────────────
@router.message(SupportSt.waiting_message)
async def support_message(msg: Message, user, state: FSMContext, bot: Bot, **kw):
    data = await state.get_data()
    support_type = data.get('support_type', 'ai')
    await state.clear()

    if support_type == 'ai':
        # AI javob
        thinking = await msg.answer("🤖 AI javob tayyorlanmoqda...")
        ai_reply = await _get_ai_reply(msg.text, user)
        await thinking.delete()

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🤖 Yana savol", callback_data="support:ai")],
            [InlineKeyboardButton(text="👨‍💼 Operatorga", callback_data="support:human")],
            [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:main")],
        ])
        await msg.answer(
            f"🤖 <b>AI Javob:</b>\n\n{ai_reply}",
            reply_markup=kb
        )

    else:
        # Adminlarga yuborish
        await _forward_to_admins(bot, msg, user)
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:main")
        ]])
        await msg.answer(
            "✅ <b>Xabaringiz qabul qilindi!</b>\n\n"
            "Operator tez orada javob beradi.\n"
            "Odatda 2-24 soat ichida.",
            reply_markup=kb
        )


async def _get_ai_reply(question: str, user) -> str:
    """AI dan support javobi."""
    try:
        from django.conf import settings as django_settings
        from openai import OpenAI
        import httpx

        key = getattr(django_settings, 'GROQ_API_KEY', '')
        if not key:
            return "Hozircha AI ishlamayapti. Operatorga murojaat qiling."

        client = OpenAI(
            api_key=key,
            base_url='https://api.groq.com/openai/v1',
            http_client=httpx.Client()
        )
        system = (
            "Sen ABT Yordamchi botining support assistantisan. "
            "O'zbek tilida qisqa va aniq javob ber. "
            "Bot haqida: IELTS, SAT, DTM tayyorgarlik boti. "
            "Premium: 29,900 so'm/oy. "
            "Savolga 3-5 gapda javob ber."
        )
        resp = client.chat.completions.create(
            model=getattr(django_settings, 'GROQ_MODEL', 'llama-3.3-70b-versatile'),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": question}
            ],
            max_tokens=400,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.error(f"Support AI: {e}")
        return (
            "Savolingiz qabul qilindi. "
            "Operatorga murojaat qiling: @ABTyordamchi1"
        )


async def _forward_to_admins(bot: Bot, msg: Message, user):
    """Adminlarga xabar yuborish."""
    from apps.users.models import User
    try:
        admins = await sync_to_async(
            lambda: list(User.objects.filter(is_staff=True).values_list('telegram_id', flat=True))
        )()
        text = (
            f"📩 <b>Support xabari</b>\n\n"
            f"👤 {user.full_name} (@{getattr(user,'username','?')})\n"
            f"🆔 ID: {user.telegram_id}\n\n"
            f"💬 {msg.text}"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="💬 Javob berish",
                url=f"tg://user?id={user.telegram_id}"
            )
        ]])
        for admin_id in admins:
            try:
                await bot.send_message(admin_id, text, reply_markup=kb)
            except Exception:
                pass
    except Exception as e:
        logger.error(f"Admin forward: {e}")