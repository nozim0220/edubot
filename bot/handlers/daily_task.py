"""Kunlik vazifa — user o'zi ham yoza oladi, eslatma yuboriladi."""
import logging
from datetime import date, time, datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async

router = Router()
logger = logging.getLogger('bot')


class DailySt(StatesGroup):
    writing_task = State()


# ── KUNLIK VAZIFA MENYU ──────────────────────────────
@router.message(F.text == "🔥 Kunlik vazifa")
@router.callback_query(F.data == "menu:daily")
async def daily_menu(event, user, state: FSMContext, **kw):
    await state.clear()
    msg = event.message if isinstance(event, CallbackQuery) else event

    # Bugungi vazifani topish
    today_task = await _get_today_task(user)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ O'zim vazifa yozaman", callback_data="daily:write")],
        [InlineKeyboardButton(text="🎯 Tasodifiy test",       callback_data="daily:random_test")],
        [InlineKeyboardButton(text="🃏 Flashcard — so'z o'rganish", callback_data="menu:flashcard")],
        [InlineKeyboardButton(text="🔔 Eslatma sozlash",      callback_data="daily:reminder")],
        [InlineKeyboardButton(text="🏠 Bosh menyu",           callback_data="menu:main")],
    ])

    if today_task:
        text = (
            f"🔥 <b>Bugungi Kunlik Vazifa</b>\n\n"
            f"📝 {today_task['text']}\n\n"
            f"⏰ Bugun: {date.today().strftime('%d.%m.%Y')}\n"
            f"{'✅ Bajarildi!' if today_task.get('done') else '⏳ Bajarilmagan'}"
        )
    else:
        text = (
            f"🔥 <b>Kunlik Vazifa</b>\n\n"
            f"📅 {date.today().strftime('%d.%m.%Y')}\n\n"
            f"Bugun uchun vazifa yo'q. O'zingiz yozing yoki\n"
            f"tasodifiy test tanlang!"
        )

    try:
        await msg.edit_text(text, reply_markup=kb)
    except Exception:
        await msg.answer(text, reply_markup=kb)

    if isinstance(event, CallbackQuery):
        await event.answer()


async def _get_today_task(user):
    """Bugungi vazifani olish."""
    try:
        from apps.education.models import DailyChallenge, UserDailyProgress
        challenge = await sync_to_async(
            DailyChallenge.objects.filter(date=date.today()).first
        )()
        if not challenge:
            return None
        test = await sync_to_async(lambda: challenge.test)()
        subj = await sync_to_async(lambda: test.subject)()
        done = await sync_to_async(
            UserDailyProgress.objects.filter(
                user=user, challenge=challenge, completed=True
            ).exists
        )()
        return {
            'text': f"{subj.emoji} {subj.name_uz} — {test.title}",
            'done': done,
            'bonus_xp': challenge.bonus_xp,
        }
    except Exception:
        return None


# ── USER O'ZI VAZIFA YOZADI ──────────────────────────
@router.callback_query(F.data == "daily:write")
async def daily_write_start(cb: CallbackQuery, state: FSMContext, **kw):
    await state.set_state(DailySt.writing_task)
    await cb.message.edit_text(
        "✍️ <b>Bugungi vazifangizni yozing</b>\n\n"
        "Misol:\n"
        "• 30 ta yangi ingliz so'z o'rganish\n"
        "• IELTS Reading 1 ta passage o'qish\n"
        "• Matematikadan 20 ta misol yechish\n\n"
        "📝 Vazifangizni yozing:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="❌ Bekor", callback_data="menu:daily")
        ]])
    )
    await cb.answer()


@router.message(DailySt.writing_task)
async def daily_save_task(msg: Message, user, state: FSMContext, **kw):
    task_text = msg.text or ""
    if len(task_text) < 5:
        await msg.answer("❌ Juda qisqa! Batafsil yozing.")
        return

    await state.clear()

    # Vazifani saqlaymiz (user note sifatida)
    try:
        await sync_to_async(_save_user_task)(user, task_text)
    except Exception as e:
        logger.debug(f"Task save: {e}")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Bajardim!", callback_data="daily:done")],
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:main")],
    ])
    await msg.answer(
        f"✅ <b>Bugungi vazifa saqlandi!</b>\n\n"
        f"📝 {task_text}\n\n"
        f"💪 Omad! Bajarganingizdan keyin ✅ bosing.",
        reply_markup=kb
    )


def _save_user_task(user, text):
    """Vazifani DB ga saqlash."""
    from apps.users.models import User
    try:
        u = User.objects.get(pk=user.pk)
        notes = u.notes or {}
        notes[str(date.today())] = {'task': text, 'done': False}
        u.notes = notes
        u.save(update_fields=['notes'])
    except Exception as e:
        logger.debug(f"Save task: {e}")


@router.callback_query(F.data == "daily:done")
async def daily_mark_done(cb: CallbackQuery, user, **kw):
    """Vazifani bajarildi deb belgilash."""
    try:
        await sync_to_async(_mark_done)(user)
        # XP berish
        await sync_to_async(user.add_xp)(50)
    except Exception as e:
        logger.debug(f"Mark done: {e}")

    await cb.message.edit_text(
        "🎉 <b>Barakalla!</b>\n\n"
        "✅ Bugungi vazifani bajardingiz!\n"
        "🎁 +50 XP qo'shildi!\n\n"
        "Ertaga ham shu ruhda davom eting! 💪",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:main")
        ]])
    )
    await cb.answer("🎉 +50 XP!")


def _mark_done(user):
    from apps.users.models import User
    try:
        u = User.objects.get(pk=user.pk)
        notes = u.notes or {}
        today = str(date.today())
        if today in notes:
            notes[today]['done'] = True
            u.notes = notes
            u.save(update_fields=['notes'])
    except Exception:
        pass


# ── TASODIFIY TEST ────────────────────────────────────
@router.callback_query(F.data == "daily:random_test")
async def daily_random_test(cb: CallbackQuery, user, state: FSMContext, **kw):
    from apps.education.models import Subject
    try:
        subjects = await sync_to_async(
            lambda: list(Subject.objects.filter(is_active=True))
        )()
        if not subjects:
            await cb.answer("Fan topilmadi!", show_alert=True); return

        import random
        subj = random.choice(subjects)
        await cb.answer(f"🎯 {subj.emoji} {subj.name_uz} tanlandi!")

        # Quiz boshlash
        from bot.handlers.education import _run_quiz
        await _run_quiz(cb, user, subj.pk, state, 'random')
    except Exception as e:
        logger.error(f"Random test: {e}")
        await cb.answer("Xato!", show_alert=True)


# ── SO'Z O'RGANISH ────────────────────────────────────
@router.callback_query(F.data == "daily:word")
async def daily_word_start(cb: CallbackQuery, state: FSMContext, **kw):
    await state.set_state(WordSt.asking_count)
    await cb.message.edit_text(
        "📖 <b>So'z o'rganish</b>\n\n"
        "Bugun nechta so'z yodlamoqchisiz?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="5 ta",  callback_data="wcount:5"),
             InlineKeyboardButton(text="10 ta", callback_data="wcount:10")],
            [InlineKeyboardButton(text="15 ta", callback_data="wcount:15"),
             InlineKeyboardButton(text="20 ta", callback_data="wcount:20")],
            [InlineKeyboardButton(text="❌ Bekor", callback_data="menu:daily")],
        ])
    )
    await cb.answer()


@router.callback_query(F.data.startswith("wcount:"))
async def word_count_chosen(cb: CallbackQuery, user, state: FSMContext, **kw):
    count = int(cb.data.split(":")[1])
    import random

    # Har user uchun unique so'zlar
    random.seed(user.telegram_id + hash(str(__import__('datetime').date.today())))
    words = random.sample(WORD_BANK, min(count, len(WORD_BANK)))

    await state.set_state(WordSt.learning)
    await state.update_data(words=words, index=0, count=count)

    await _show_word(cb.message, words, 0, edit=True)
    await cb.answer()


async def _show_word(msg, words, index, edit=False):
    word, meaning, example = words[index]
    total = len(words)
    text = (
        f"📖 <b>{index+1}/{total} — So'z o'rganish</b>\n\n"
        f"🔤 <b>{word}</b>\n"
        f"📝 {meaning}\n\n"
        f"💬 <i>{example}</i>\n\n"
        f"💡 Bu so'zni 3 marta o'qing!"
    )
    if index + 1 < total:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Keyingi so'z", callback_data=f"wnext:{index+1}")],
            [InlineKeyboardButton(text="❌ To'xtatish", callback_data="menu:daily")],
        ])
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ O'rgandim! Test boshlash", callback_data="wtest:start")],
            [InlineKeyboardButton(text="🔄 Qayta ko'rish", callback_data="wnext:0")],
        ])
    if edit:
        try:
            await msg.edit_text(text, reply_markup=kb)
        except Exception:
            await msg.answer(text, reply_markup=kb)
    else:
        await msg.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("wnext:"))
async def word_next(cb: CallbackQuery, state: FSMContext, **kw):
    index = int(cb.data.split(":")[1])
    data  = await state.get_data()
    words = data.get('words', [])
    await state.update_data(index=index)
    await _show_word(cb.message, words, index, edit=True)
    await cb.answer()


@router.callback_query(F.data == "wtest:start")
async def word_test_start(cb: CallbackQuery, state: FSMContext, **kw):
    data  = await state.get_data()
    words = data.get('words', [])
    import random

    # 5 ta test savol yaratish
    test_words = random.sample(words, min(5, len(words)))
    tests = []
    for w, meaning, _ in test_words:
        # To'g'ri javob + 3 ta noto'g'ri
        wrong = [m for ww, m, _ in words if ww != w]
        random.shuffle(wrong)
        opts = [meaning] + wrong[:3]
        random.shuffle(opts)
        tests.append({'word': w, 'answer': meaning, 'opts': opts})

    await state.set_state(WordSt.testing)
    await state.update_data(tests=tests, t_index=0, t_correct=0)
    await _show_test(cb.message, tests, 0, edit=True)
    await cb.answer()


async def _show_test(msg, tests, index, edit=False):
    t     = tests[index]
    total = len(tests)
    opts  = t['opts']
    letters = ['A', 'B', 'C', 'D']
    text = (
        f"🧪 <b>Test {index+1}/{total}</b>\n\n"
        f"🔤 <b>{t['word']}</b> — ma'nosi nima?\n\n"
        + "\n".join(f"{letters[i]}) {opts[i]}" for i in range(len(opts)))
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=letters[i], callback_data=f"wans:{index}:{i}")
         for i in range(len(opts))]
    ])
    if edit:
        try:
            await msg.edit_text(text, reply_markup=kb)
        except Exception:
            await msg.answer(text, reply_markup=kb)
    else:
        await msg.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("wans:"))
async def word_answer(cb: CallbackQuery, user, state: FSMContext, **kw):
    parts   = cb.data.split(":")
    t_index = int(parts[1])
    chosen  = int(parts[2])
    data    = await state.get_data()
    tests   = data.get('tests', [])
    correct = data.get('t_correct', 0)

    t        = tests[t_index]
    is_ok    = t['opts'][chosen] == t['answer']
    if is_ok:
        correct += 1
    await state.update_data(t_correct=correct)

    feedback = "✅ To'g'ri!" if is_ok else f"❌ Noto'g'ri! To'g'ri: <b>{t['answer']}</b>"

    if t_index + 1 < len(tests):
        await cb.message.edit_text(
            feedback,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="➡️ Keyingi", callback_data=f"wtest:{t_index+1}")
            ]])
        )
    else:
        await state.clear()
        xp = correct * 10
        try:
            await sync_to_async(user.add_xp)(xp)
        except Exception:
            pass
        await cb.message.edit_text(
            f"{feedback}\n\n"
            f"🏁 <b>Test yakunlandi!</b>\n"
            f"✅ {correct}/{len(tests)} to'g'ri\n"
            f"🎁 +{xp} XP",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Yana o'rganish", callback_data="daily:word")],
                [InlineKeyboardButton(text="🏠 Menyu", callback_data="menu:main")],
            ])
        )
    await cb.answer(feedback[:30])


@router.callback_query(F.data.startswith("wtest:"), ~F.data.in_({"wtest:start"}))
async def word_test_next(cb: CallbackQuery, state: FSMContext, **kw):
    index = int(cb.data.split(":")[1])
    data  = await state.get_data()
    tests = data.get('tests', [])
    if not tests or index >= len(tests):
        await cb.answer("Sessiya tugagan, qaytadan boshlang!", show_alert=True)
        await state.clear()
        await cb.message.edit_text(
            "⚠️ Sessiya tugagan.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🔄 Qayta boshlash", callback_data="daily:word")
            ]])
        )
        return
    await _show_test(cb.message, tests, index, edit=True)
    await cb.answer()


# ── ESLATMA SOZLASH ───────────────────────────────────
@router.callback_query(F.data == "daily:reminder")
async def daily_reminder(cb: CallbackQuery, user, **kw):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌅 07:00 ertalab", callback_data="reminder:07:00")],
        [InlineKeyboardButton(text="🌞 09:00 ertalab", callback_data="reminder:09:00")],
        [InlineKeyboardButton(text="🌆 18:00 kechqurun", callback_data="reminder:18:00")],
        [InlineKeyboardButton(text="🌙 20:00 kechqurun", callback_data="reminder:20:00")],
        [InlineKeyboardButton(text="❌ Eslatmani o'chirish", callback_data="reminder:off")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:daily")],
    ])
    current = getattr(user, 'reminder_time', None)
    text = (
        f"🔔 <b>Kunlik eslatma</b>\n\n"
        f"Hozirgi: <b>{current or 'O\'chirilgan'}</b>\n\n"
        f"Qaysi vaqtda eslatma olishni xohlaysiz?"
    )
    await cb.message.edit_text(text, reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data.startswith("reminder:"))
async def set_reminder(cb: CallbackQuery, user, **kw):
    val = cb.data.split(":")[1]

    try:
        await sync_to_async(_save_reminder)(user, None if val == "off" else val+":00")
    except Exception as e:
        logger.debug(f"Reminder save: {e}")

    if val == "off":
        msg = "❌ Eslatma o'chirildi."
    else:
        msg = f"✅ Eslatma {val}:00 ga sozlandi!"

    await cb.answer(msg, show_alert=True)

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:daily")
    ]])
    await cb.message.edit_text(
        f"🔔 <b>Eslatma sozlandi</b>\n\n{msg}\n\n"
        f"Har kuni shu vaqtda sizga xabar yuboramiz.",
        reply_markup=kb
    )


def _save_reminder(user, reminder_time):
    from apps.users.models import User
    try:
        User.objects.filter(pk=user.pk).update(reminder_time=reminder_time)
    except Exception:
        pass


# ── ESLATMA YUBORISH (Celery task) ────────────────────
async def send_daily_reminders(bot: Bot):
    """Barcha userlarga eslatma yuborish — scheduler dan chaqiriladi."""
    from apps.users.models import User
    from django.utils import timezone

    current_hour = timezone.now().hour
    current_time = f"{current_hour:02d}:00:00"

    try:
        users = await sync_to_async(
            lambda: list(User.objects.filter(
                is_active=True,
                reminder_time=current_time
            ).values('telegram_id', 'first_name'))
        )()

        for u in users:
            try:
                await bot.send_message(
                    u['telegram_id'],
                    f"🔔 <b>Kunlik eslatma!</b>\n\n"
                    f"Salom {u['first_name']}! 👋\n"
                    f"Bugun o'qish uchun vaqt ajrating.\n\n"
                    f"💪 Har kun bir qadam — maqsad sari!",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                        InlineKeyboardButton(text="🔥 Bugungi vazifa", callback_data="menu:daily")
                    ]])
                )
            except Exception:
                pass

        logger.info(f"Eslatmalar yuborildi: {len(users)} ta user")
    except Exception as e:
        logger.error(f"Send reminders: {e}")