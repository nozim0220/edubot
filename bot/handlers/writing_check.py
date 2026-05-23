"""IELTS Writing AI baholash."""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()
logger = logging.getLogger('bot')


class WritingSt(StatesGroup):
    task1 = State()
    task2 = State()


@router.callback_query(F.data == "menu:writing")
@router.message(F.text == "✍️ Writing")
async def writing_menu(event, user, **kw):
    msg = event.message if isinstance(event, CallbackQuery) else event
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Task 1 — Grafik/Jadval tavsifi", callback_data="writing:task1")],
        [InlineKeyboardButton(text="📝 Task 2 — Esse yozish",           callback_data="writing:task2")],
        [InlineKeyboardButton(text="🏠 Bosh menyu",                     callback_data="menu:main")],
    ])
    text = (
        "✍️ <b>IELTS Writing</b>\n\n"
        "AI esseyingizni 4 mezon bo'yicha baholaydi:\n"
        "• Task Achievement\n"
        "• Coherence & Cohesion\n"
        "• Lexical Resource\n"
        "• Grammatical Range\n\n"
        "Qaysi task?"
    )
    try:
        await msg.edit_text(text, reply_markup=kb)
    except Exception:
        await msg.answer(text, reply_markup=kb)
    if isinstance(event, CallbackQuery):
        await event.answer()


@router.callback_query(F.data == "writing:task1")
async def writing_task1_start(cb: CallbackQuery, state: FSMContext, **kw):
    await state.set_state(WritingSt.task1)
    await cb.message.edit_text(
        "📊 <b>IELTS Writing Task 1</b>\n\n"
        "Vazifa: Grafik, jadval yoki diagrammani tasvirlab bering.\n\n"
        "📌 Namuna prompt:\n"
        "<i>The chart shows the percentage of students who passed their driving test "
        "in different years (2000: 45%, 2005: 52%, 2010: 61%, 2015: 58%, 2020: 67%)</i>\n\n"
        "✍️ Esseyingizni yozing (kamida 150 so'z):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="❌ Bekor", callback_data="menu:writing")
        ]])
    )
    await cb.answer()


@router.callback_query(F.data == "writing:task2")
async def writing_task2_start(cb: CallbackQuery, state: FSMContext, **kw):
    await state.set_state(WritingSt.task2)
    await cb.message.edit_text(
        "📝 <b>IELTS Writing Task 2</b>\n\n"
        "Vazifa: Quyidagi mavzuda esse yozing:\n\n"
        "<i>Some people believe that technology has made our lives more complicated. "
        "Others think that technology has simplified our lives. "
        "Discuss both views and give your own opinion.</i>\n\n"
        "✍️ Esseyingizni yozing (kamida 250 so'z):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="❌ Bekor", callback_data="menu:writing")
        ]])
    )
    await cb.answer()


@router.message(WritingSt.task1)
@router.message(WritingSt.task2)
async def writing_check(msg: Message, user, state: FSMContext, **kw):
    current = await state.get_state()
    task_num = 1 if current == WritingSt.task1 else 2
    essay = msg.text or ""
    word_count = len(essay.split())
    min_words = 150 if task_num == 1 else 250

    if word_count < 50:
        await msg.answer(
            f"❌ Juda qisqa! Kamida {min_words} so'z yozing.\n"
            f"Hozir: {word_count} so'z"
        )
        return

    await state.clear()
    thinking = await msg.answer("🤖 AI baholayapti... ⏳")

    result = await _ai_grade_essay(essay, task_num, word_count)
    await thinking.delete()

    # XP berish
    xp = 30 if word_count >= min_words else 10
    try:
        from asgiref.sync import sync_to_async
        await sync_to_async(user.add_xp)(xp)
    except Exception:
        pass

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Yana yozish", callback_data=f"writing:task{task_num}")],
        [InlineKeyboardButton(text="🏠 Bosh menyu",  callback_data="menu:main")],
    ])
    await msg.answer(
        f"✍️ <b>Writing Task {task_num} — Baho</b>\n\n"
        f"📝 So'zlar: {word_count}\n\n"
        f"{result}\n\n"
        f"🎁 +{xp} XP",
        reply_markup=kb
    )


async def _ai_grade_essay(essay: str, task_num: int, word_count: int) -> str:
    try:
        from django.conf import settings
        from openai import OpenAI
        import httpx

        key = getattr(settings, 'GROQ_API_KEY', '')
        if not key:
            return _simple_grade(word_count, task_num)

        client = OpenAI(
            api_key=key,
            base_url='https://api.groq.com/openai/v1',
            http_client=httpx.Client()
        )
        prompt = (
            f"IELTS Writing Task {task_num} esseyni baholang.\n\n"
            f"ESSE ({word_count} so'z):\n{essay[:2000]}\n\n"
            f"O'zbek tilida quyidagi formatda baho bering:\n\n"
            f"📊 Umumiy band: X.X/9.0\n\n"
            f"✅ Task Achievement: X/9\n"
            f"✅ Coherence & Cohesion: X/9\n"
            f"✅ Lexical Resource: X/9\n"
            f"✅ Grammar: X/9\n\n"
            f"💪 Kuchli tomonlar:\n• ...\n\n"
            f"⚠️ Kamchiliklar:\n• ...\n\n"
            f"💡 Yaxshilash uchun:\n• ..."
        )
        resp = client.chat.completions.create(
            model=getattr(settings, 'GROQ_MODEL', 'llama-3.3-70b-versatile'),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.error(f"Writing AI: {e}")
        return _simple_grade(word_count, task_num)


def _simple_grade(word_count: int, task_num: int) -> str:
    min_w = 150 if task_num == 1 else 250
    if word_count >= min_w:
        band = min(7.0, 5.0 + (word_count - min_w) * 0.005)
        return f"📊 Taxminiy band: {band:.1f}/9.0\n✅ So'zlar yetarli!"
    return f"⚠️ Kamida {min_w} so'z kerak. Hozir: {word_count}"