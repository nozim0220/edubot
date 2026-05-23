"""Ta'lim handler — fanlar, testlar, kundalik vazifa, o'rganish."""
import logging, random
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async
from bot.keyboards.main import back_keyboard

router = Router()
logger = logging.getLogger('bot')


class QuizState(StatesGroup):
    in_quiz = State()

class DailyState(StatesGroup):
    selecting_subject = State()
    in_daily = State()


@router.callback_query(F.data == "menu:education")
async def education_menu(cb: CallbackQuery, user, **kw):
    from apps.education.models import Subject, UserProgress
    subjects = await sync_to_async(list)(Subject.objects.filter(is_active=True))
    user_subj_ids = await sync_to_async(
        lambda: list(UserProgress.objects.filter(user=user).values_list('subject_id', flat=True))
    )()
    buttons = []
    row = []
    for s in subjects:
        done = "✅" if s.id in user_subj_ids else "📖"
        row.append(InlineKeyboardButton(text=f"{done} {s.emoji} {s.name_uz}", callback_data=f"subject:{s.id}"))
        if len(row) == 2:
            buttons.append(row); row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:main")])
    await cb.message.edit_text(
        "📚 <b>Ta'lim</b>\n\nFan tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("subject:"))
async def subject_menu(cb: CallbackQuery, user, **kw):
    from apps.education.models import Subject, UserProgress, Question
    sid = int(cb.data.split(":")[1])
    subj = await sync_to_async(Subject.objects.get)(pk=sid, is_active=True)
    qcount = await sync_to_async(Question.objects.filter(subject=subj, is_active=True).count)()
    try:
        p = await sync_to_async(UserProgress.objects.get)(user=user, subject=subj)
        stats = f"\n📊 {p.tests_completed} test | {p.accuracy_rate}% | {p.total_xp} XP"
    except Exception:
        stats = ""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎯 Test",        callback_data=f"edu:quiz:{sid}"),
            InlineKeyboardButton(text="🎲 Random 10",   callback_data=f"edu:random:{sid}"),
        ],
        [InlineKeyboardButton(text="📊 Natijalarim",    callback_data=f"edu:progress:{sid}")],
        [InlineKeyboardButton(text="🤖 AI tushuntirsin",callback_data=f"edu:ai:{sid}")],
        [InlineKeyboardButton(text="🔙 Orqaga",         callback_data="menu:education")],
    ])
    await cb.message.edit_text(
        f"{subj.emoji} <b>{subj.name_uz}</b>\n"
        f"📚 {qcount} ta savol{stats}",
        reply_markup=kb,
    )
    await cb.answer()


async def _run_quiz(cb: CallbackQuery, user, subject_id: int, state: FSMContext, mode: str):
    from apps.education.models import Subject, Test, Question, TestSession, TestQuestion
    from apps.education.services import QuizService

    subj = await sync_to_async(Subject.objects.get)(pk=subject_id)

    if mode == 'random':
        qs = await sync_to_async(
            lambda: list(Question.objects.filter(subject=subj, is_active=True).order_by('?')[:10])
        )()
        if not qs:
            await cb.answer("Bu fanda savollar yo'q!", show_alert=True); return
        test = await sync_to_async(Test.objects.create)(
            title_uz=f"Random — {subj.name_uz}", subject=subj,
            test_type='random', passing_score=60, is_active=True,
        )
        for i, q in enumerate(qs):
            await sync_to_async(TestQuestion.objects.create)(test=test, question=q, order=i)
    else:
        test = await sync_to_async(
            lambda: Test.objects.filter(subject=subj, test_type=mode, is_active=True).first()
        )()
        if not test:
            await cb.answer("Bu fanda test yo'q!", show_alert=True); return
        qs = await sync_to_async(
            lambda: list(test.questions.filter(is_active=True).order_by('testquestion__order'))
        )()

    if not qs:
        await cb.answer("Savollar topilmadi!", show_alert=True); return

    session = await sync_to_async(QuizService.start_test_session)(user, test)
    await state.set_state(QuizState.in_quiz)
    await state.update_data(
        session_id=session.pk,
        questions=[q.pk for q in qs],
        current=0,
        subject_id=subject_id,
    )
    await _send_quiz_q(cb.message, qs[0], 1, len(qs), session.pk, edit=True)
    await cb.answer()


@router.callback_query(F.data.startswith("edu:quiz:"))
async def start_quiz(cb: CallbackQuery, user, state: FSMContext, **kw):
    await _run_quiz(cb, user, int(cb.data.split(":")[2]), state, 'quiz')

@router.callback_query(F.data.startswith("edu:random:"))
async def start_random(cb: CallbackQuery, user, state: FSMContext, **kw):
    await _run_quiz(cb, user, int(cb.data.split(":")[2]), state, 'random')


async def _send_quiz_q(msg, q, num: int, total: int, session_id: int, edit: bool = False):
    text = f"❓ <b>{num}/{total}</b>\n\n{q.text_uz}\n"
    opts = []
    if q.option_a: opts.append(("A", q.option_a))
    if q.option_b: opts.append(("B", q.option_b))
    if q.option_c: opts.append(("C", q.option_c))
    if q.option_d: opts.append(("D", q.option_d))
    for l, o in opts:
        text += f"\n  <b>{l})</b> {o}"
    btns = [InlineKeyboardButton(text=l, callback_data=f"ans:{session_id}:{q.pk}:{l}") for l, _ in opts]
    kb = InlineKeyboardMarkup(inline_keyboard=[btns] if btns else [])
    if edit:
        try: await msg.edit_text(text, reply_markup=kb)
        except: await msg.answer(text, reply_markup=kb)
    else:
        await msg.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("ans:"), QuizState.in_quiz)
async def quiz_answer(cb: CallbackQuery, user, state: FSMContext, **kw):
    from apps.education.services import QuizService
    from apps.education.models import TestSession, Question

    parts = cb.data.split(":")
    session_id, question_id, answer = int(parts[1]), int(parts[2]), parts[3]

    data = await state.get_data()
    if not data or data.get('session_id') != session_id:
        await cb.answer("Sessiya topilmadi!", show_alert=True); return

    try:
        session = await sync_to_async(TestSession.objects.get)(pk=session_id, user=user)
        result  = await sync_to_async(QuizService.submit_answer)(session, question_id, answer)
    except Exception as e:
        logger.error(f"Quiz answer error: {e}")
        await cb.answer("Xato!", show_alert=True); return

    is_ok    = result.get('is_correct', False)
    correct_a= result.get('correct_answer', '?')
    exp      = result.get('explanation_uz', '')
    feedback = f"{'✅ To\'g\'ri!' if is_ok else f'❌ Noto\'g\'ri! Javob: <b>{correct_a}</b>'}"
    if exp: feedback += f"\n💡 {exp}"

    questions = data['questions']
    current   = data['current'] + 1
    subject_id= data['subject_id']
    await state.update_data(current=current)

    if current >= len(questions):
        final = await sync_to_async(QuizService.complete_session)(session)
        await state.clear()
        score = final['score']
        passed = "✅ O'tdingiz!" if final['passed'] else "❌ O'tmadingiz"

        # AI rag'batlantirish
        ai_tip = ""
        try:
            from bot.handlers.ai_assistant import _send_ai_quick
            ai_tip = await _send_ai_quick(
                user,
                f"Test natijasi {final['correct_answers']}/{final['total_questions']} ({score}%). "
                f"Qisqa (2 gap) rag'batlantiruvchi xabar yoz."
            )
        except Exception:
            pass

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Qayta",   callback_data=f"edu:quiz:{subject_id}"),
                InlineKeyboardButton(text="📚 Fanlar",  callback_data="menu:education"),
            ],
            [InlineKeyboardButton(text="🏠 Menyu", callback_data="menu:main")],
        ])
        text = (
            f"{feedback}\n\n"
            f"🏁 <b>Test tugadi!</b>\n"
            f"📊 {final['correct_answers']}/{final['total_questions']} ({score}%)\n"
            f"⭐ {passed}  🎁 +{final['xp_earned']} XP"
        )
        if ai_tip:
            text += f"\n\n🤖 {ai_tip}"
        await cb.message.edit_text(text, reply_markup=kb)
    else:
        q_id = questions[current]
        q    = await sync_to_async(Question.objects.get)(pk=q_id)
        # Yakunlash tugmasi bilan feedback
        finish_kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text=f"🏁 Yakunlash ({current}/{len(questions)})",
                callback_data=f"quiz:finish:{session_id}:{subject_id}"
            )
        ]])
        await cb.message.edit_text(feedback, reply_markup=finish_kb)
        await _send_quiz_q(cb.message, q, current + 1, len(questions), session_id)
    await cb.answer()


@router.callback_query(F.data.startswith("quiz:finish:"))
async def quiz_finish_early(cb: CallbackQuery, user, state: FSMContext, **kw):
    """Testni vaqtidan oldin yakunlash."""
    from apps.education.services import QuizService
    from apps.education.models import TestSession

    parts = cb.data.split(":")
    session_id = int(parts[2])
    subject_id = int(parts[3])

    try:
        session = await sync_to_async(TestSession.objects.get)(pk=session_id, user=user)
        final   = await sync_to_async(QuizService.complete_session)(session)
        await state.clear()
        score  = final['score']
        passed = "✅ O'tdingiz!" if final['passed'] else "❌ O'tmadingiz"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Qayta",  callback_data=f"edu:quiz:{subject_id}"),
                InlineKeyboardButton(text="📚 Fanlar", callback_data="menu:education"),
            ],
            [InlineKeyboardButton(text="🏠 Menyu", callback_data="menu:main")],
        ])
        text = (
            "🏁 <b>Test yakunlandi!</b>\n"
            f"📊 {final['correct_answers']}/{final['total_questions']} ({score}%)\n"
            f"⭐ {passed}  🎁 +{final['xp_earned']} XP"
        )
        await cb.message.edit_text(text, reply_markup=kb)
    except Exception as e:
        await cb.answer("Xato!", show_alert=True)
    await cb.answer()


@router.callback_query(F.data.startswith("edu:progress:"))
async def subject_progress(cb: CallbackQuery, user, **kw):
    from apps.education.models import UserProgress, Subject
    sid  = int(cb.data.split(":")[2])
    subj = await sync_to_async(Subject.objects.get)(pk=sid)
    try:
        p = await sync_to_async(UserProgress.objects.get)(user=user, subject=subj)
        text = (
            f"📊 <b>{subj.emoji} {subj.name_uz}</b>\n\n"
            f"✅ Testlar: {p.tests_completed}\n"
            f"❓ Savollar: {p.questions_answered}\n"
            f"🎯 To'g'ri: {p.correct_answers}\n"
            f"📈 Aniqlik: {p.accuracy_rate}%\n"
            f"🏆 Eng yaxshi: {p.best_score}%\n"
            f"⭐ Jami XP: {p.total_xp}"
        )
    except Exception:
        text = f"{subj.emoji} {subj.name_uz}\n\nHali test ishlamadingiz."
    await cb.message.edit_text(text, reply_markup=back_keyboard(f"subject:{sid}"))
    await cb.answer()


@router.callback_query(F.data.startswith("edu:ai:"))
async def edu_ai_explain(cb: CallbackQuery, user, **kw):
    from apps.education.models import Subject
    from bot.handlers.ai_assistant import _send_ai_quick
    sid  = int(cb.data.split(":")[2])
    subj = await sync_to_async(Subject.objects.get)(pk=sid)
    await cb.message.answer("🤖 AI tayyorlanmoqda...")
    tip = await _send_ai_quick(
        user,
        f"{subj.name_uz} fanini o'rganish bo'yicha 5 ta qisqa maslahat ber (o'zbek tilida)."
    )
    if tip:
        await cb.message.answer(
            f"🤖 <b>{subj.emoji} {subj.name_uz} — AI maslahati:</b>\n\n{tip}",
            reply_markup=back_keyboard(f"subject:{sid}"),
        )
    await cb.answer()


# ── KUNDALIK VAZIFA ──────────────────────────────────
@router.callback_query(F.data == "menu:daily_old")
async def daily_menu(cb: CallbackQuery, user, state: FSMContext, **kw):
    from apps.education.models import Subject, UserProgress, DailyChallenge
    from datetime import date

    # Bugun challenge bor?
    today_challenge = await sync_to_async(
        lambda: DailyChallenge.objects.filter(date=date.today()).first()
    )()

    # User o'z fanlarini tanlashi
    subjects = await sync_to_async(list)(Subject.objects.filter(is_active=True))
    buttons  = []
    row = []
    for s in subjects:
        row.append(InlineKeyboardButton(
            text=f"{s.emoji} {s.name_uz}",
            callback_data=f"daily:sub:{s.id}"
        ))
        if len(row) == 2:
            buttons.append(row); row = []
    if row: buttons.append(row)

    if today_challenge:
        test = await sync_to_async(lambda: today_challenge.test)()
        subj = await sync_to_async(lambda: test.subject)()
        buttons.insert(0, [InlineKeyboardButton(
            text=f"🔥 Bugungi vazifa: {subj.emoji} {subj.name_uz} (+{today_challenge.bonus_xp} XP)",
            callback_data=f"daily:today"
        )])

    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:main")])

    await cb.message.edit_text(
        "🔥 <b>Kundalik vazifa</b>\n\n"
        "Fan tanlang — har kuni 10 savol, bonus XP!\n"
        "Streak uchun har kuni bajaring 🏆",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await cb.answer()


@router.callback_query(F.data == "daily:today")
async def daily_today(cb: CallbackQuery, user, state: FSMContext, **kw):
    from apps.education.models import DailyChallenge
    from datetime import date
    challenge = await sync_to_async(
        lambda: DailyChallenge.objects.filter(date=date.today()).first()
    )()
    if not challenge:
        await cb.answer("Bugungi vazifa yo'q!", show_alert=True); return
    test = challenge.test
    subj = await sync_to_async(lambda: test.subject)()
    # Quiz sifatida boshlash
    from apps.education.models import Question, TestSession, TestQuestion
    from apps.education.services import QuizService
    qs = await sync_to_async(
        lambda: list(test.questions.filter(is_active=True)[:10])
    )()
    if not qs:
        await cb.answer("Savollar yo'q!", show_alert=True); return
    session = await sync_to_async(QuizService.start_test_session)(user, test)
    await state.set_state(QuizState.in_quiz)
    await state.update_data(
        session_id=session.pk,
        questions=[q.pk for q in qs],
        current=0,
        subject_id=subj.pk,
    )
    await _send_quiz_q(cb.message, qs[0], 1, len(qs), session.pk, edit=True)
    await cb.answer()


@router.callback_query(F.data.startswith("daily:sub:"))
async def daily_by_subject(cb: CallbackQuery, user, state: FSMContext, **kw):
    from apps.education.models import Subject, Question, Test, TestQuestion
    from apps.education.services import QuizService
    sid  = int(cb.data.split(":")[2])
    subj = await sync_to_async(Subject.objects.get)(pk=sid)
    # User avval ko'rgan savollarni chiqarish
    from apps.education.models import TestSession
    seen_q_ids = await sync_to_async(
        lambda: list(
            TestSession.objects.filter(user=user, status='completed')
            .values_list('answers', flat=True)
        )
    )()
    answered_ids = []
    for ans_dict in seen_q_ids:
        if isinstance(ans_dict, dict):
            answered_ids.extend(ans_dict.keys())

    qs = await sync_to_async(
        lambda: list(
            Question.objects.filter(subject=subj, is_active=True)
            .exclude(pk__in=[int(i) for i in answered_ids if str(i).isdigit()])
            .order_by('?')[:10]
        )
    )()
    # Agar yetarli savol qolmasa, hammasidan olish
    if len(qs) < 5:
        qs = await sync_to_async(
            lambda: list(Question.objects.filter(subject=subj, is_active=True).order_by('?')[:10])
        )()
    if not qs:
        await cb.answer("Bu fanda savollar yo'q!", show_alert=True); return

    test = await sync_to_async(Test.objects.create)(
        title_uz=f"Kundalik — {subj.name_uz}",
        subject=subj, test_type='quiz', passing_score=60, is_active=True,
    )
    for i, q in enumerate(qs):
        await sync_to_async(TestQuestion.objects.create)(test=test, question=q, order=i)

    session = await sync_to_async(QuizService.start_test_session)(user, test)
    await state.set_state(QuizState.in_quiz)
    await state.update_data(
        session_id=session.pk,
        questions=[q.pk for q in qs],
        current=0,
        subject_id=sid,
    )
    await _send_quiz_q(cb.message, qs[0], 1, len(qs), session.pk, edit=True)
    await cb.answer()


async def education_menu_msg(msg, user):
    """ReplyKeyboard tugmasidan kelgan education menu."""
    from apps.education.models import Subject, UserProgress
    subjects = await sync_to_async(list)(Subject.objects.filter(is_active=True))
    user_subj_ids = await sync_to_async(
        lambda: list(UserProgress.objects.filter(user=user).values_list('subject_id', flat=True))
    )()
    buttons = []
    row = []
    for s in subjects:
        done = "✅" if s.id in user_subj_ids else "📖"
        row.append(InlineKeyboardButton(text=f"{done} {s.emoji} {s.name_uz}", callback_data=f"subject:{s.id}"))
        if len(row) == 2:
            buttons.append(row); row = []
    if row: buttons.append(row)
    await msg.answer("📚 <b>Ta'lim</b>\n\nFan tanlang:",
                     reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


async def daily_menu_msg(msg, user, state):
    """ReplyKeyboard tugmasidan kelgan daily menu."""
    from apps.education.models import Subject, DailyChallenge
    from datetime import date
    subjects = await sync_to_async(list)(Subject.objects.filter(is_active=True))
    buttons  = []
    row = []
    today_challenge = await sync_to_async(
        lambda: DailyChallenge.objects.filter(date=date.today()).first()
    )()
    for s in subjects:
        row.append(InlineKeyboardButton(text=f"{s.emoji} {s.name_uz}", callback_data=f"daily:sub:{s.id}"))
        if len(row) == 2: buttons.append(row); row = []
    if row: buttons.append(row)
    if today_challenge:
        test = await sync_to_async(lambda: today_challenge.test)()
        subj = await sync_to_async(lambda: test.subject)()
        buttons.insert(0, [InlineKeyboardButton(
            text=f"🔥 Bugungi vazifa: {subj.emoji} {subj.name_uz} (+{today_challenge.bonus_xp} XP)",
            callback_data="daily:today"
        )])
    await msg.answer(
        "🔥 <b>Kunlik vazifa</b>\n\nFan tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )