"""Imtihon sanasi countdown va motivatsiya."""
import logging
from datetime import date, datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async

router = Router()
logger = logging.getLogger('bot')


class CountdownSt(StatesGroup):
    setting_date = State()


EXAM_TYPES = {
    'ielts': '🎓 IELTS',
    'sat':   '🎯 SAT',
    'dtm':   '📊 DTM',
    'other': '📝 Boshqa',
}

MOTIVATIONS = [
    "💪 Har bir daqiqa qimmat — davom eting!",
    "🔥 Maqsad aniq — yo'l ochiq. Ishla!",
    "⭐ Bugungi mehnat — ertangi muvaffaqiyat!",
    "🚀 Hech narsa imkonsiz emas — faqat harakat kerak!",
    "🎯 Maqsadingizga har kuni bir qadam yaqinlashing!",
    "💎 Qiyinchilik — kuchlilarni sinovchi imkon!",
    "🌟 Sen buni udda qila olasiz — ishon o'zingga!",
    "📚 Bilim — eng yaxshi investitsiya!",
    "🏆 Rekordi sindirish uchun bugun ishlang!",
    "✨ Har sabah yangi imkoniyat — qo'ldan bermang!",
]


@router.callback_query(F.data == "menu:countdown")
async def countdown_menu(cb: CallbackQuery, user, **kw):
    await _show_countdown(cb.message, user, edit=True)
    await cb.answer()


async def _show_countdown(msg, user, edit=False):
    exam_date = await sync_to_async(_get_exam_date)(user)

    if exam_date:
        today = date.today()
        days_left = (exam_date['date'] - today).days
        exam_name = EXAM_TYPES.get(exam_date['type'], '📝 Imtihon')

        if days_left < 0:
            text = (
                f"🎓 <b>{exam_name}</b>\n\n"
                f"✅ Imtihon o'tib ketdi!\n"
                f"Yangi sana belgilaysizmi?"
            )
        elif days_left == 0:
            text = (
                f"🎓 <b>{exam_name}</b>\n\n"
                f"🔥 <b>BUGUN IMTIHON!</b>\n"
                f"Omad tilaymiz! 💪"
            )
        else:
            # Progress bar
            total_days = exam_date.get('total_days', 100)
            passed = max(0, total_days - days_left)
            progress = min(10, int(passed / max(total_days, 1) * 10))
            bar = "🟩" * progress + "⬜" * (10 - progress)

            text = (
                f"⏰ <b>{exam_name} sanasi</b>\n\n"
                f"📅 Sana: <b>{exam_date['date'].strftime('%d.%m.%Y')}</b>\n"
                f"⏳ Qoldi: <b>{days_left} kun</b>\n\n"
                f"{bar} {int(passed/max(total_days,1)*100)}%\n\n"
                f"💡 Har kuni o'qing!"
            )
    else:
        text = (
            "⏰ <b>Imtihon sanasi</b>\n\n"
            "Imtihon sanangizni belgilang —\n"
            "countdown va eslatmalar ishlaydi!"
        )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Sana belgilash", callback_data="countdown:set")],
        [InlineKeyboardButton(text="🏠 Bosh menyu",     callback_data="menu:main")],
    ])

    try:
        if edit:
            await msg.edit_text(text, reply_markup=kb)
        else:
            await msg.answer(text, reply_markup=kb)
    except Exception:
        await msg.answer(text, reply_markup=kb)


@router.callback_query(F.data == "countdown:set")
async def countdown_set(cb: CallbackQuery, state: FSMContext, **kw):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=f"countdown:type:{key}")]
        for key, name in EXAM_TYPES.items()
    ] + [[InlineKeyboardButton(text="❌ Bekor", callback_data="menu:countdown")]])

    await state.set_state(CountdownSt.setting_date)
    await cb.message.edit_text(
        "📅 <b>Imtihon turini tanlang:</b>",
        reply_markup=kb
    )
    await cb.answer()


@router.callback_query(F.data.startswith("countdown:type:"))
async def countdown_type(cb: CallbackQuery, state: FSMContext, **kw):
    exam_type = cb.data.split(":")[2]
    await state.update_data(exam_type=exam_type)
    await cb.message.edit_text(
        f"📅 <b>{EXAM_TYPES.get(exam_type)} sanasini kiriting</b>\n\n"
        f"Format: <b>DD.MM.YYYY</b>\n"
        f"Masalan: <code>15.08.2026</code>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="❌ Bekor", callback_data="menu:countdown")
        ]])
    )
    await cb.answer()


@router.message(CountdownSt.setting_date)
async def countdown_save(msg: Message, user, state: FSMContext, **kw):
    text = msg.text or ""
    data = await state.get_data()
    exam_type = data.get('exam_type', 'other')

    try:
        exam_date = datetime.strptime(text.strip(), "%d.%m.%Y").date()
        if exam_date < date.today():
            await msg.answer("❌ O'tgan sana! Kelajakdagi sana kiriting.")
            return
    except ValueError:
        await msg.answer("❌ Noto'g'ri format! DD.MM.YYYY ko'rinishida yozing.\nMasalan: 15.08.2026")
        return

    await state.clear()
    days_left = (exam_date - date.today()).days

    await sync_to_async(_save_exam_date)(user, exam_date, exam_type, days_left)

    exam_name = EXAM_TYPES.get(exam_type, '📝 Imtihon')
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⏰ Countdown ko'rish", callback_data="menu:countdown")
    ]])
    await msg.answer(
        f"✅ <b>{exam_name} sanasi saqlandi!</b>\n\n"
        f"📅 {exam_date.strftime('%d.%m.%Y')}\n"
        f"⏳ {days_left} kun qoldi\n\n"
        f"🔔 Har kuni eslatma yuboriladi!",
        reply_markup=kb
    )


def _get_exam_date(user):
    from apps.users.models import User
    try:
        u = User.objects.get(pk=user.pk)
        notes = u.notes or {}
        exam = notes.get('exam_date')
        if exam:
            return {
                'date': date.fromisoformat(exam['date']),
                'type': exam.get('type', 'other'),
                'total_days': exam.get('total_days', 100),
            }
    except Exception:
        pass
    return None


def _save_exam_date(user, exam_date, exam_type, total_days):
    from apps.users.models import User
    try:
        u = User.objects.get(pk=user.pk)
        notes = u.notes or {}
        notes['exam_date'] = {
            'date': exam_date.isoformat(),
            'type': exam_type,
            'total_days': total_days,
        }
        u.notes = notes
        u.save(update_fields=['notes'])
    except Exception as e:
        logger.error(f"Save exam date: {e}")


async def send_countdown_reminders(bot: Bot):
    """Har kuni imtihon sanasi eslatmasi."""
    from apps.users.models import User
    import random

    try:
        users = await sync_to_async(
            lambda: list(User.objects.filter(is_active=True).exclude(notes={}))
        )()

        for user in users:
            notes = user.notes or {}
            exam = notes.get('exam_date')
            if not exam:
                continue

            try:
                exam_date = date.fromisoformat(exam['date'])
                days_left = (exam_date - date.today()).days

                if days_left < 0:
                    continue

                exam_name = EXAM_TYPES.get(exam.get('type', 'other'), '📝 Imtihon')
                motivation = random.choice(MOTIVATIONS)

                if days_left == 0:
                    text = f"🔥 <b>Bugun {exam_name}!</b>\n\nOmad! 💪"
                elif days_left <= 7:
                    text = (
                        f"⏰ <b>{exam_name} ga {days_left} kun qoldi!</b>\n\n"
                        f"{motivation}"
                    )
                elif days_left % 7 == 0 or days_left in [30, 14, 10, 5, 3, 1]:
                    text = (
                        f"📅 <b>{exam_name} ga {days_left} kun qoldi</b>\n\n"
                        f"{motivation}"
                    )
                else:
                    continue

                await bot.send_message(
                    user.telegram_id, text,
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                        InlineKeyboardButton(text="📚 O'qishni boshlash", callback_data="menu:education")
                    ]])
                )
            except Exception:
                pass
    except Exception as e:
        logger.error(f"Countdown reminders: {e}")