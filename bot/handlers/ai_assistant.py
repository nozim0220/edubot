"""AI Yordamchi handler — hamma narsaga bog'liq."""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async

from bot.keyboards.main import back_keyboard

router = Router()
logger = logging.getLogger('bot')

AI_TYPES = {
    'ai:homework':    ('homework',   "📝 Uy ishi yordam"),
    'ai:math':        ('math',       "🧮 Matematik masala"),
    'ai:explain':     ('explain',    "📖 Mavzuni tushuntir"),
    'ai:grammar':     ('grammar',    "✍️ Grammatika tekshir"),
    'ai:essay':       ('essay',      "📄 Insho yozish"),
    'ai:career':      ('career',     "🎯 Karyera maslahat"),
    'ai:study_plan':  ('study_plan', "📅 O'qish rejasi"),
    'ai:general':     ('general',    "💬 Erkin suhbat"),
}

PROMPTS = {
    'homework':   "Uy ishingizni yozing (fan nomi ham yozsangiz yaxshi):",
    'math':       "Matematik masalani to'liq yozing:",
    'explain':    "Qaysi mavzuni tushuntirish kerak?",
    'grammar':    "Tekshirilishi kerak bo'lgan matnni yozing:",
    'essay':      "Insho mavzusini yozing:",
    'career':     "Karyera bo'yicha savolingizni yozing:",
    'study_plan': "Qaysi imtihonga, qancha vaqt bor?",
    'general':    "Savolingizni yozing:",
}


class AIState(StatesGroup):
    chatting = State()


async def _send_ai_quick(user, prompt: str) -> str:
    """Tez AI so'rov — boshqa handlerlar uchun."""
    try:
        from apps.ai_assistant.services import AIService, get_ai_client, get_client
        client, model = get_ai_client()
        if not client:
            return ""
        from apps.ai_assistant.models import AIChat
        chat = await sync_to_async(AIChat.objects.create)(
            user=user, chat_type='general', title='Quick'
        )
        result = await sync_to_async(AIService().send_message)(user, chat, prompt)
        return result.get('response', '')
    except Exception as e:
        logger.error(f"Quick AI xato: {e}")
        return ""


@router.callback_query(F.data == "menu:ai")
async def ai_menu(callback: CallbackQuery, user, **kwargs):
    from apps.ai_assistant.services import AIService
    service = AIService()
    stats = await sync_to_async(service.get_usage_stats)(user)

    if not user.is_premium_active:
        usage_line = f"\n\n📊 Bugun: {stats['used_today']}/{stats['limit']} so'rov"
    else:
        usage_line = f"\n\n💎 Premium: {stats['used_today']}/{stats['limit']} so'rov"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Uy ishi",       callback_data="ai:homework"),
            InlineKeyboardButton(text="🧮 Matematika",    callback_data="ai:math"),
        ],
        [
            InlineKeyboardButton(text="📖 Tushuntir",     callback_data="ai:explain"),
            InlineKeyboardButton(text="✍️ Grammatika",    callback_data="ai:grammar"),
        ],
        [
            InlineKeyboardButton(text="📄 Insho",         callback_data="ai:essay"),
            InlineKeyboardButton(text="🎯 Karyera",       callback_data="ai:career"),
        ],
        [
            InlineKeyboardButton(text="📅 O'qish rejasi", callback_data="ai:study_plan"),
            InlineKeyboardButton(text="💬 Erkin suhbat",  callback_data="ai:general"),
        ],
        [InlineKeyboardButton(text="📋 Saqlangan chatlar", callback_data="ai:history")],
        [InlineKeyboardButton(text="🔙 Orqaga",            callback_data="menu:main")],
    ])
    await callback.message.edit_text(
        f"🤖 <b>AI Yordamchi</b>\n\nNima haqida yordam kerak?{usage_line}",
        reply_markup=kb,
    )
    await callback.answer()


@router.callback_query(F.data.in_(AI_TYPES.keys()))
async def ai_type_select(callback: CallbackQuery, user, state: FSMContext, **kwargs):
    chat_type, label = AI_TYPES[callback.data]
    from apps.ai_assistant.services import AIService
    service = AIService()
    chat = await sync_to_async(service.get_or_create_chat)(user=user, chat_type=chat_type)

    await state.set_state(AIState.chatting)
    await state.update_data(chat_id=chat.pk, chat_type=chat_type)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⏹ Tugatish",  callback_data="ai:stop"),
            InlineKeyboardButton(text="💾 Saqlash",   callback_data="ai:save"),
        ],
    ])
    await callback.message.edit_text(
        f"🤖 <b>{label}</b>\n\n{PROMPTS.get(chat_type, 'Savolingizni yozing:')}\n\n"
        f"<i>Tugatish: ⏹ tugma yoki /stop</i>",
        reply_markup=kb,
    )
    await callback.answer()


@router.message(AIState.chatting)
async def ai_chat(message: Message, user, state: FSMContext, **kwargs):
    if message.text and message.text.strip().lower() in ('/stop', 'stop'):
        await state.clear()
        await message.answer("✅ Chat tugatildi.", reply_markup=back_keyboard("menu:ai"))
        return

    data = await state.get_data()
    chat_id = data.get('chat_id')

    thinking = await message.answer("🤔 <i>Javob tayyorlanmoqda...</i>")

    try:
        from apps.ai_assistant.services import AIService
        from apps.ai_assistant.models import AIChat
        service = AIService()
        chat = await sync_to_async(AIChat.objects.get)(pk=chat_id, user=user)
        result = await sync_to_async(service.send_message)(
            user=user, chat=chat, user_message=message.text or ""
        )
        await thinking.delete()

        response = result['response']
        remaining = result['remaining_requests']

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⏹ Tugatish", callback_data="ai:stop"),
                InlineKeyboardButton(text="💾 Saqlash",  callback_data="ai:save"),
            ],
        ])

        # Uzun javoblarni bo'lib yuborish
        if len(response) > 4000:
            for i in range(0, len(response), 4000):
                chunk = response[i:i+4000]
                if i + 4000 >= len(response):
                    await message.answer(chunk, reply_markup=kb)
                else:
                    await message.answer(chunk)
        else:
            await message.answer(response, reply_markup=kb)

        if remaining <= 3 and not user.is_premium_active:
            await message.answer(
                f"⚠️ Kunlik limitdan <b>{remaining}</b> ta so'rov qoldi!\n"
                f"💎 /premium — cheksiz foydalanish"
            )

    except Exception as e:
        await thinking.delete()
        err = str(e)
        if 'limit' in err.lower() or 'quota' in err.lower():
            await message.answer(
                "⚠️ <b>Kunlik limit tugadi!</b>\n\n"
                "💎 Premium oling — cheksiz AI so'rovlar:\n/premium",
                reply_markup=back_keyboard("menu:ai"),
            )
            await state.clear()
        elif 'sozlanmagan' in err or 'api_key_xato' in err or 'unavailable' in err.lower():
            await message.answer(
                "❌ <b>AI sozlanmagan!</b>\n\n"
                "📌 Groq (bepul) API key oling:\n"
                "👉 https://console.groq.com\n\n"
                "1️⃣ Saytga kiring\n"
                "2️⃣ API Keys → Create API Key\n"
                "3️⃣ <code>gsk_...</code> key ni nusxalang\n"
                "4️⃣ <code>.env</code> faylida:\n"
                "<code>GROQ_API_KEY=gsk_siz_olgan_key</code>\n\n"
                "5️⃣ Botni qayta ishga tushiring"
            )
        elif 'rate_limit' in err:
            await message.answer("⏳ Juda ko'p so'rov yuborildi. 30 soniya kuting.")
        else:
            await message.answer(f"❌ Xato: {err[:300]}")


@router.callback_query(F.data == "ai:stop")
async def ai_stop(callback: CallbackQuery, state: FSMContext, **kwargs):
    await state.clear()
    await callback.message.edit_text(
        "✅ Chat tugatildi.",
        reply_markup=back_keyboard("menu:ai"),
    )
    await callback.answer()


@router.callback_query(F.data == "ai:save")
async def ai_save(callback: CallbackQuery, user, state: FSMContext, **kwargs):
    data = await state.get_data()
    chat_id = data.get('chat_id')
    if chat_id:
        from apps.ai_assistant.models import AIChat
        await sync_to_async(
            lambda: AIChat.objects.filter(pk=chat_id, user=user).update(is_saved=True)
        )()
        await callback.answer("💾 Chat saqlandi!", show_alert=True)
    else:
        await callback.answer("Chat topilmadi.", show_alert=True)


@router.callback_query(F.data == "ai:history")
async def ai_history(callback: CallbackQuery, user, **kwargs):
    from apps.ai_assistant.models import AIChat
    chats = await sync_to_async(
        lambda: list(AIChat.objects.filter(user=user, is_saved=True).order_by('-updated_at')[:10])
    )()
    if not chats:
        await callback.message.edit_text(
            "📋 Saqlangan chatlar yo'q.\n\nChat davomida '💾 Saqlash' tugmasini bosing.",
            reply_markup=back_keyboard("menu:ai"),
        )
        await callback.answer()
        return

    buttons = [
        [InlineKeyboardButton(text=f"💬 {c.title[:40]}", callback_data=f"ai:view:{c.pk}")]
        for c in chats
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:ai")])
    await callback.message.edit_text(
        "📋 <b>Saqlangan chatlar:</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ai:view:"))
async def ai_view_chat(callback: CallbackQuery, user, state: FSMContext, **kwargs):
    chat_id = int(callback.data.split(":")[2])
    from apps.ai_assistant.models import AIChat, AIMessage
    try:
        chat = await sync_to_async(AIChat.objects.get)(pk=chat_id, user=user)
        messages = await sync_to_async(
            lambda: list(AIMessage.objects.filter(chat=chat).order_by('-created_at')[:6])
        )()
        messages.reverse()
        text = f"💬 <b>{chat.title}</b>\n\n"
        for m in messages:
            icon = "👤" if m.role == 'user' else "🤖"
            content = m.content[:300] + ("..." if len(m.content) > 300 else "")
            text += f"{icon} {content}\n\n"

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Davom ettirish", callback_data=f"ai:continue:{chat_id}")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="ai:history")],
        ])
        await callback.message.edit_text(text, reply_markup=kb)
    except Exception:
        await callback.answer("Chat topilmadi!", show_alert=True)
    await callback.answer()


@router.callback_query(F.data.startswith("ai:continue:"))
async def ai_continue(callback: CallbackQuery, user, state: FSMContext, **kwargs):
    chat_id = int(callback.data.split(":")[2])
    from apps.ai_assistant.models import AIChat
    chat = await sync_to_async(AIChat.objects.get)(pk=chat_id, user=user)
    await state.set_state(AIState.chatting)
    await state.update_data(chat_id=chat.pk, chat_type=chat.chat_type)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⏹ Tugatish", callback_data="ai:stop"),
            InlineKeyboardButton(text="💾 Saqlash",  callback_data="ai:save"),
        ],
    ])
    await callback.message.edit_text(
        f"🤖 <b>{chat.title}</b>\n\nDavom eting...",
        reply_markup=kb,
    )
    await callback.answer()
