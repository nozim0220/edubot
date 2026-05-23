"""Admin handler — filtersiz, ichida tekshiruv bilan."""
import logging
from aiogram import Router, F
from aiogram.types import (CallbackQuery, Message,
                            InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async

router = Router()
# ⚠️ Router darajasida filter YO'Q — har bir handlerda o'zi tekshiradi
logger = logging.getLogger('bot')


class BroadcastSt(StatesGroup):
    audience = State()
    text     = State()
    confirm  = State()


class AddQSt(StatesGroup):
    subject    = State()
    text       = State()
    opt_a      = State()
    opt_b      = State()
    opt_c      = State()
    opt_d      = State()
    correct    = State()
    difficulty = State()


class AddMockSt(StatesGroup):
    exam_type = State(); subject = State()
    passage = State(); q_text = State()
    opt_a = State(); opt_b = State(); opt_c = State(); opt_d = State()
    correct = State(); difficulty = State()


class GiveAdminSt(StatesGroup):
    waiting_id = State()


async def _check_admin(user) -> bool:
    """Admin tekshirish."""
    if not user:
        return False
    return bool(user.is_admin or user.is_staff)


def adm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="adm:users"),
            InlineKeyboardButton(text="📊 Statistika",        callback_data="adm:stats"),
        ],
        [
            InlineKeyboardButton(text="📢 Broadcast",         callback_data="adm:broadcast"),
            InlineKeyboardButton(text="❓ Savol qo'shish",    callback_data="adm:add_q"),
        ],
        [
            InlineKeyboardButton(text="🔥 Kunlik vazifa",     callback_data="adm:daily"),
            InlineKeyboardButton(text="👑 Admin berish",      callback_data="adm:give_admin"),
        ],
        [InlineKeyboardButton(text="💎 Premium berish",       callback_data="adm:give_premium")],
        [InlineKeyboardButton(text="🔄 Bot restart",         callback_data="adm:restart_confirm")],
        [InlineKeyboardButton(text="🔙 Bosh menyu",           callback_data="menu:main")],
    ])


async def _show_panel(msg, send=False, edit=False):
    from apps.users.models import User as U
    total   = await sync_to_async(U.objects.count)()
    premium = await sync_to_async(U.objects.filter(is_premium=True).count)()
    banned  = await sync_to_async(U.objects.filter(status='banned').count)()
    text = (
        f"🔐 <b>Admin Panel</b>\n\n"
        f"👥 Jami: {total} | 💎 Premium: {premium} | 🚫 Ban: {banned}"
    )
    if send:
        await msg.answer(text, reply_markup=adm_kb())
    elif edit:
        try:
            await msg.edit_text(text, reply_markup=adm_kb())
        except Exception:
            await msg.answer(text, reply_markup=adm_kb())
    else:
        await msg.answer(text, reply_markup=adm_kb())


# ── /admin BUYRUQ ─────────────────────────────────────
@router.message(F.text == "/admin")
async def admin_cmd(msg: Message, user, **kw):
    if not await _check_admin(user):
        await msg.answer("❌ Sizda admin huquqi yo'q!")
        return
    await _show_panel(msg, send=True)


# ── ADMIN PANEL CALLBACK ──────────────────────────────
@router.callback_query(F.data == "adm:panel")
async def adm_panel_cb(cb: CallbackQuery, user, **kw):
    if not await _check_admin(user):
        await cb.answer("❌ Admin huquqi yo'q!", show_alert=True)
        return
    await _show_panel(cb.message, edit=True)
    await cb.answer()


# ── STATISTIKA ────────────────────────────────────────
@router.callback_query(F.data == "adm:stats")
async def adm_stats(cb: CallbackQuery, user, **kw):
    if not await _check_admin(user):
        await cb.answer("❌", show_alert=True); return
    from apps.users.models import User as U
    from django.utils import timezone
    from datetime import timedelta, date
    now   = timezone.now()
    today = date.today()
    week  = now - timedelta(days=7)
    total     = await sync_to_async(U.objects.count)()
    new_today = await sync_to_async(U.objects.filter(date_joined__date=today).count)()
    new_week  = await sync_to_async(U.objects.filter(date_joined__gte=week).count)()
    active    = await sync_to_async(U.objects.filter(last_seen__gte=week).count)()
    premium   = await sync_to_async(U.objects.filter(is_premium=True).count)()
    with_ielts= await sync_to_async(U.objects.filter(ielts_score__isnull=False).count)()
    with_dtm  = await sync_to_async(U.objects.filter(dtm_score__isnull=False).count)()
    await cb.message.edit_text(
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Jami: <b>{total}</b>\n"
        f"🆕 Bugun: <b>{new_today}</b>\n"
        f"📅 Haftalik: <b>{new_week}</b>\n"
        f"⚡ Faol (7 kun): <b>{active}</b>\n"
        f"💎 Premium: <b>{premium}</b>\n"
        f"📝 IELTS bor: <b>{with_ielts}</b>\n"
        f"📊 DTM bor: <b>{with_dtm}</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm:panel")]
        ])
    )
    await cb.answer()


# ── FOYDALANUVCHILAR ──────────────────────────────────
@router.callback_query(F.data == "adm:users")
async def adm_users(cb: CallbackQuery, user, **kw):
    if not await _check_admin(user):
        await cb.answer("❌", show_alert=True); return
    from apps.users.models import User as U
    users = await sync_to_async(
        lambda: list(U.objects.order_by('-date_joined')[:15])
    )()
    btns = []
    for u in users:
        prem = "💎" if u.is_premium else ""
        ban  = "🚫" if u.status == 'banned' else ""
        adm  = "👑" if u.is_admin else ""
        name = f"{u.first_name or ''} {u.last_name or ''}".strip() or f"ID:{u.telegram_id}"
        btns.append([InlineKeyboardButton(
            text=f"{ban}{prem}{adm} {name[:30]}",
            callback_data=f"adm:user:{u.pk}"
        )])
    btns.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm:panel")])
    await cb.message.edit_text(
        f"👥 <b>So'nggi {len(users)} foydalanuvchi:</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=btns)
    )
    await cb.answer()


@router.callback_query(F.data.startswith("adm:user:"))
async def adm_user_detail(cb: CallbackQuery, user, **kw):
    if not await _check_admin(user):
        await cb.answer("❌", show_alert=True); return
    pk = int(cb.data.split(":")[2])
    from apps.users.models import User as U
    u  = await sync_to_async(U.objects.get)(pk=pk)
    certs = u.get_certificates_summary()
    goal_map = {'uzbekistan': "🇺🇿 O'zbekistonda", 'abroad': "✈️ Chet elda", 'both': "🌐 Ikkalasi"}
    text = (
        f"👤 <b>{u.full_name}</b>\n"
        f"🆔 <code>{u.telegram_id}</code>\n"
        f"📱 {u.phone_number or '—'}\n"
        f"📍 {u.region or '—'} / {u.city or '—'}\n"
        f"🏫 {u.school or '—'} | {u.grade or '—'}\n"
        f"🎯 {goal_map.get(u.study_goal, '—')}\n"
        f"🎓 {u.dream_university or '—'}\n"
        f"📜 {', '.join(certs) if certs else '—'}\n"
        f"⭐ XP: {u.xp_points} | Lv.{u.level} | 🔥 {u.study_streak} kun\n"
        f"💎 Premium: {'Ha' if u.is_premium else 'Yo\'q'}\n"
        f"👑 Admin: {'Ha' if u.is_admin else 'Yo\'q'}\n"
        f"🔰 Status: {u.status}\n"
        f"📅 {u.date_joined.strftime('%d.%m.%Y')}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚫 Ban",       callback_data=f"adm:ban:{pk}"),
            InlineKeyboardButton(text="✅ Unban",      callback_data=f"adm:unban:{pk}"),
        ],
        [InlineKeyboardButton(text="👑 Admin berish", callback_data=f"adm:makead:{pk}")],
        [InlineKeyboardButton(text="🔙 Orqaga",       callback_data="adm:users")],
    ])
    await cb.message.edit_text(text, reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data.startswith("adm:ban:"))
async def adm_ban(cb: CallbackQuery, user, **kw):
    if not await _check_admin(user):
        await cb.answer("❌", show_alert=True); return
    pk = int(cb.data.split(":")[2])
    from apps.users.models import User as U
    await sync_to_async(U.objects.filter(pk=pk).update)(status='banned')
    await cb.answer("🚫 Bloklandi!", show_alert=True)
    await adm_user_detail(cb, user=user)


@router.callback_query(F.data.startswith("adm:unban:"))
async def adm_unban(cb: CallbackQuery, user, **kw):
    if not await _check_admin(user):
        await cb.answer("❌", show_alert=True); return
    pk = int(cb.data.split(":")[2])
    from apps.users.models import User as U
    await sync_to_async(U.objects.filter(pk=pk).update)(status='active')
    await cb.answer("✅ Blok olib tashlandi!", show_alert=True)
    await adm_user_detail(cb, user=user)


@router.callback_query(F.data.startswith("adm:makead:"))
async def adm_make_admin(cb: CallbackQuery, user, **kw):
    if not await _check_admin(user):
        await cb.answer("❌", show_alert=True); return
    pk = int(cb.data.split(":")[2])
    from apps.users.models import User as U
    await sync_to_async(U.objects.filter(pk=pk).update)(is_admin=True, is_staff=True)
    target = await sync_to_async(U.objects.get)(pk=pk)
    await cb.answer(f"👑 {target.full_name} — Admin!", show_alert=True)
    await adm_user_detail(cb, user=user)


# ── ADMIN BERISH ──────────────────────────────────────
@router.callback_query(F.data == "adm:give_admin")
async def give_admin_start(cb: CallbackQuery, user, state: FSMContext, **kw):
    if not await _check_admin(user):
        await cb.answer("❌", show_alert=True); return
    await state.set_state(GiveAdminSt.waiting_id)
    await cb.message.edit_text(
        "👑 <b>Admin berish</b>\n\n"
        "Telegram ID kiriting:\n"
        "📌 ID bilish: @userinfobot ga /start yuboring",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="adm:give_cancel")]
        ])
    )
    await cb.answer()


@router.message(GiveAdminSt.waiting_id)
async def give_admin_do(msg: Message, user, state: FSMContext, **kw):
    if not await _check_admin(user):
        await state.clear(); return
    await state.clear()
    try:
        tg_id  = int(msg.text.strip())
        from apps.users.models import User as U
        target = await sync_to_async(U.objects.get)(telegram_id=tg_id)
        await sync_to_async(U.objects.filter(pk=target.pk).update)(is_admin=True, is_staff=True)
        await msg.answer(
            f"✅ <b>{target.full_name}</b> — Admin qilindi!\n"
            f"ID: <code>{tg_id}</code>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Admin panel", callback_data="adm:panel")]
            ])
        )
    except Exception as e:
        await msg.answer(
            f"❌ Topilmadi!\nID: <code>{msg.text}</code>\n\nFoydalanuvchi avval botga /start bosishi kerak.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Admin panel", callback_data="adm:panel")]
            ])
        )


# ── BROADCAST ─────────────────────────────────────────
@router.callback_query(F.data == "adm:broadcast")
async def broadcast_start(cb: CallbackQuery, user, state: FSMContext, **kw):
    if not await _check_admin(user):
        await cb.answer("❌", show_alert=True); return
    await state.set_state(BroadcastSt.audience)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Hammaga",        callback_data="bc_aud:all")],
        [InlineKeyboardButton(text="⚡ Faolga (7 kun)",  callback_data="bc_aud:active")],
        [InlineKeyboardButton(text="🔙 Orqaga",          callback_data="adm:panel")],
    ])
    await cb.message.edit_text("📢 <b>Kimga yuborasiz?</b>", reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data.startswith("bc_aud:"), BroadcastSt.audience)
async def bc_audience(cb: CallbackQuery, state: FSMContext, **kw):
    await state.update_data(audience=cb.data.split(":")[1])
    await state.set_state(BroadcastSt.text)
    await cb.message.edit_text("📝 <b>Xabar matnini yozing:</b>")
    await cb.answer()


@router.message(BroadcastSt.text)
async def bc_text(msg: Message, state: FSMContext, **kw):
    await state.update_data(text=msg.text)
    await state.set_state(BroadcastSt.confirm)
    data = await state.get_data()
    aud  = {'all': 'Hammaga', 'active': 'Faollarga'}.get(data.get('audience', 'all'))
    kb   = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yuborish",      callback_data="bc:send"),
            InlineKeyboardButton(text="❌ Bekor",         callback_data="bc:cancel"),
        ],
        [InlineKeyboardButton(text="🗑 Xabarni o'chirish", callback_data="bc:delete_msg")],
    ])
    await msg.answer(
        f"📢 <b>Tasdiqlang:</b>\nKimga: {aud}\n\n{msg.text[:400]}",
        reply_markup=kb
    )


@router.callback_query(F.data == "bc:send", BroadcastSt.confirm)
async def bc_send(cb: CallbackQuery, user, state: FSMContext, bot, **kw):
    if not await _check_admin(user):
        await cb.answer("❌", show_alert=True); return
    data = await state.get_data()
    await state.clear()
    from apps.users.models import User as U
    aud  = data.get('audience', 'all')
    text = data.get('text', '')
    qs   = U.objects.filter(is_active=True, status='active')
    if aud == 'active':
        from django.utils import timezone
        from datetime import timedelta
        qs = qs.filter(last_seen__gte=timezone.now() - timedelta(days=7))
    tg_ids = await sync_to_async(list)(qs.values_list('telegram_id', flat=True))
    sent = 0
    for tg_id in tg_ids:
        try:
            await bot.send_message(tg_id, text)
            sent += 1
        except Exception:
            pass
    await cb.message.edit_text(
        f"✅ Yuborildi: <b>{sent}/{len(tg_ids)}</b> ta",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Admin panel", callback_data="adm:panel")]
        ])
    )
    await cb.answer()
    # Broadcast xabarini o'chirish (tasdiqlash xabari)
    try:
        await cb.message.delete()
    except Exception:
        pass


@router.callback_query(F.data == "bc:cancel")
async def bc_cancel(cb: CallbackQuery, user, state: FSMContext, **kw):
    await state.clear()
    await _show_panel(cb.message, edit=True)
    await cb.answer()


# ── SAVOL QO'SHISH ────────────────────────────────────
@router.callback_query(F.data == "adm:add_q")
async def add_q_start(cb: CallbackQuery, user, state: FSMContext, **kw):
    if not await _check_admin(user):
        await cb.answer("❌", show_alert=True); return
    from apps.education.models import Subject
    subjects = await sync_to_async(list)(Subject.objects.filter(is_active=True))
    rows = []
    r = []
    for s in subjects:
        r.append(InlineKeyboardButton(text=f"{s.emoji} {s.name_uz}", callback_data=f"aq_s:{s.pk}"))
        if len(r) == 2: rows.append(r); r = []
    if r: rows.append(r)
    rows.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm:panel")])
    await state.set_state(AddQSt.subject)
    await cb.message.edit_text(
        "❓ <b>Savol qo'shish</b>\n\nFan tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )
    await cb.answer()


@router.callback_query(F.data.startswith("aq_s:"), AddQSt.subject)
async def aq_subj(cb: CallbackQuery, state: FSMContext, **kw):
    await state.update_data(subject_id=int(cb.data.split(":")[1]))
    await state.set_state(AddQSt.text)
    await cb.message.edit_text("📝 Savol matnini kiriting:")
    await cb.answer()


@router.message(AddQSt.text)
async def aq_text(msg: Message, state: FSMContext, **kw):
    await state.update_data(text=msg.text)
    await state.set_state(AddQSt.opt_a)
    await msg.answer("A) variantni kiriting:")


@router.message(AddQSt.opt_a)
async def aq_a(msg: Message, state: FSMContext, **kw):
    await state.update_data(opt_a=msg.text)
    await state.set_state(AddQSt.opt_b)
    await msg.answer("B) variantni kiriting:")


@router.message(AddQSt.opt_b)
async def aq_b(msg: Message, state: FSMContext, **kw):
    await state.update_data(opt_b=msg.text)
    await state.set_state(AddQSt.opt_c)
    await msg.answer("C) variantni kiriting:")


@router.message(AddQSt.opt_c)
async def aq_c(msg: Message, state: FSMContext, **kw):
    await state.update_data(opt_c=msg.text)
    await state.set_state(AddQSt.opt_d)
    await msg.answer("D) variantni kiriting:")


@router.message(AddQSt.opt_d)
async def aq_d(msg: Message, state: FSMContext, **kw):
    await state.update_data(opt_d=msg.text)
    await state.set_state(AddQSt.correct)
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=l, callback_data=f"aq_ans:{l}")
        for l in ["A", "B", "C", "D"]
    ]])
    await msg.answer("✅ To'g'ri javobni tanlang:", reply_markup=kb)


@router.callback_query(F.data.startswith("aq_ans:"), AddQSt.correct)
async def aq_correct(cb: CallbackQuery, state: FSMContext, **kw):
    await state.update_data(correct=cb.data.split(":")[1])
    await state.set_state(AddQSt.difficulty)
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🟢 Oson",  callback_data="aq_dif:easy"),
        InlineKeyboardButton(text="🟡 O'rta", callback_data="aq_dif:medium"),
        InlineKeyboardButton(text="🔴 Qiyin", callback_data="aq_dif:hard"),
    ]])
    await cb.message.edit_text("📊 Qiyinlik darajasi:", reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data.startswith("aq_dif:"), AddQSt.difficulty)
async def aq_save(cb: CallbackQuery, state: FSMContext, **kw):
    data = await state.get_data()
    await state.clear()
    from apps.education.models import Question
    q = await sync_to_async(Question.objects.create)(
        subject_id=data['subject_id'],
        text_uz=data['text'],
        option_a=data['opt_a'],
        option_b=data['opt_b'],
        option_c=data['opt_c'],
        option_d=data['opt_d'],
        correct_answer=data['correct'],
        difficulty=cb.data.split(":")[1],
        is_active=True,
        xp_reward=10,
    )
    await cb.message.edit_text(
        f"✅ Savol qo'shildi! (ID: {q.pk})",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Yana qo'shish", callback_data="adm:add_q")],
            [InlineKeyboardButton(text="🔙 Admin panel",   callback_data="adm:panel")],
        ])
    )
    await cb.answer()


# ── KUNLIK VAZIFA ─────────────────────────────────────
@router.callback_query(F.data == "adm:daily")
async def adm_daily(cb: CallbackQuery, user, **kw):
    if not await _check_admin(user):
        await cb.answer("❌", show_alert=True); return
    from apps.education.models import Test, DailyChallenge
    from datetime import date
    import random
    today  = date.today()
    exists = await sync_to_async(DailyChallenge.objects.filter(date=today).exists)()
    if exists:
        await cb.answer("✅ Bugungi vazifa allaqachon bor!", show_alert=True)
        return
    tests = await sync_to_async(
        lambda: list(Test.objects.filter(is_active=True)[:20])
    )()
    if not tests:
        await cb.answer("❌ Testlar yo'q!", show_alert=True)
        return
    test = random.choice(tests)
    await sync_to_async(DailyChallenge.objects.create)(date=today, test=test, bonus_xp=100)
    await cb.answer(f"✅ Qo'shildi: {test.title_uz[:30]}", show_alert=True)
    await _show_panel(cb.message, edit=True)


@router.callback_query(F.data == "bc:delete_msg")
async def bc_delete_msg(cb: CallbackQuery, state: FSMContext, **kw):
    """Broadcast xabarini o'chirish."""
    await state.clear()
    try:
        await cb.message.delete()
    except Exception:
        pass
    await cb.answer("🗑 Xabar o'chirildi")


@router.callback_query(F.data == "adm:give_cancel")
async def give_admin_cancel(cb: CallbackQuery, state: FSMContext, **kw):
    """Admin berish - bekor qilish."""
    await state.clear()
    await _show_panel(cb.message, edit=True)
    await cb.answer("❌ Bekor qilindi")


# ── MOCK SAVOL QO'SHISH ──────────────────────────────
@router.callback_query(F.data == "adm:add_mock")
async def add_mock_start(cb: CallbackQuery, user, state: FSMContext, **kw):
    if not await _check_admin(user):
        await cb.answer("❌", show_alert=True); return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 IELTS Reading",   callback_data="mock_type:ielts_r")],
        [InlineKeyboardButton(text="🎧 IELTS Listening", callback_data="mock_type:ielts_l")],
        [InlineKeyboardButton(text="📊 DTM savol",       callback_data="mock_type:dtm")],
        [InlineKeyboardButton(text="🔢 SAT savol",       callback_data="mock_type:sat")],
        [InlineKeyboardButton(text="🔙 Orqaga",          callback_data="adm:panel")],
    ])
    await state.set_state(AddMockSt.exam_type)
    await cb.message.edit_text("❓ <b>Qaysi turdagi mock savol?</b>", reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data.startswith("mock_type:"), AddMockSt.exam_type)
async def mock_type_picked(cb: CallbackQuery, state: FSMContext, **kw):
    mtype = cb.data.split(":")[1]
    await state.update_data(mock_type=mtype)
    await state.set_state(AddMockSt.subject)

    type_map = {
        'ielts_r': 'ielts', 'ielts_l': 'ielts',
        'dtm': None, 'sat': 'sat'
    }
    if mtype == 'dtm':
        from apps.education.models import Subject
        subjects = await sync_to_async(list)(Subject.objects.filter(is_active=True))
        rows = []
        r = []
        for s in subjects:
            r.append(InlineKeyboardButton(text=f"{s.emoji} {s.name_uz}", callback_data=f"mock_subj:{s.pk}"))
            if len(r) == 2: rows.append(r); r = []
        if r: rows.append(r)
        await cb.message.edit_text("📚 Fan tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    else:
        code = type_map.get(mtype, 'ielts')
        from apps.education.models import Subject
        subj = await sync_to_async(Subject.objects.filter(code=code).first)()
        if subj:
            await state.update_data(subject_id=subj.pk)
        await state.set_state(AddMockSt.q_text)
        await cb.message.edit_text("📝 Savol matnini kiriting:")
    await cb.answer()


@router.callback_query(F.data.startswith("mock_subj:"), AddMockSt.subject)
async def mock_subj_picked(cb: CallbackQuery, state: FSMContext, **kw):
    await state.update_data(subject_id=int(cb.data.split(":")[1]))
    await state.set_state(AddMockSt.q_text)
    await cb.message.edit_text("📝 Savol matnini kiriting:")
    await cb.answer()


@router.message(AddMockSt.q_text)
async def mock_q_text(msg: Message, state: FSMContext, **kw):
    await state.update_data(q_text=msg.text)
    await state.set_state(AddMockSt.opt_a)
    await msg.answer("A) variantni kiriting:")


@router.message(AddMockSt.opt_a)
async def mock_opt_a(msg: Message, state: FSMContext, **kw):
    await state.update_data(opt_a=msg.text); await state.set_state(AddMockSt.opt_b)
    await msg.answer("B) variantni kiriting:")

@router.message(AddMockSt.opt_b)
async def mock_opt_b(msg: Message, state: FSMContext, **kw):
    await state.update_data(opt_b=msg.text); await state.set_state(AddMockSt.opt_c)
    await msg.answer("C) variantni kiriting:")

@router.message(AddMockSt.opt_c)
async def mock_opt_c(msg: Message, state: FSMContext, **kw):
    await state.update_data(opt_c=msg.text); await state.set_state(AddMockSt.opt_d)
    await msg.answer("D) variantni kiriting:")

@router.message(AddMockSt.opt_d)
async def mock_opt_d(msg: Message, state: FSMContext, **kw):
    await state.update_data(opt_d=msg.text)
    await state.set_state(AddMockSt.correct)
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=l, callback_data=f"mock_ans_c:{l}")
        for l in ["A","B","C","D"]
    ]])
    await msg.answer("✅ To'g'ri javob:", reply_markup=kb)


@router.callback_query(F.data.startswith("mock_ans_c:"), AddMockSt.correct)
async def mock_correct(cb: CallbackQuery, state: FSMContext, **kw):
    await state.update_data(correct=cb.data.split(":")[1])
    await state.set_state(AddMockSt.difficulty)
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🟢 Oson", callback_data="mock_dif:easy"),
        InlineKeyboardButton(text="🟡 O'rta", callback_data="mock_dif:medium"),
        InlineKeyboardButton(text="🔴 Qiyin", callback_data="mock_dif:hard"),
    ]])
    await cb.message.edit_text("📊 Qiyinlik:", reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data.startswith("mock_dif:"), AddMockSt.difficulty)
async def mock_save(cb: CallbackQuery, state: FSMContext, **kw):
    data = await state.get_data()
    await state.clear()
    from apps.education.models import Question
    q = await sync_to_async(Question.objects.create)(
        subject_id=data['subject_id'],
        text_uz=data['q_text'],
        option_a=data['opt_a'], option_b=data['opt_b'],
        option_c=data['opt_c'], option_d=data['opt_d'],
        correct_answer=data['correct'],
        difficulty=cb.data.split(":")[1],
        is_active=True, xp_reward=15,
    )
    await cb.message.edit_text(
        f"✅ Mock savol qo'shildi! ID: {q.pk}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Yana", callback_data="adm:add_mock")],
            [InlineKeyboardButton(text="🔙 Admin", callback_data="adm:panel")],
        ])
    )
    await cb.answer()


# ── BOT RESTART ──────────────────────────────────────
@router.callback_query(F.data == "adm:restart")
async def bot_restart(cb: CallbackQuery, user, state: FSMContext, **kw):
    if not await _check_admin(user):
        await cb.answer("❌ Ruxsat yo'q", show_alert=True); return

    import asyncio, os, sys

    # Cache tozalash
    try:
        from django.core.cache import cache
        cache.clear()
    except Exception:
        pass

    # FSM tozalash
    await state.clear()

    await cb.message.edit_text(
        "🔄 <b>Bot qayta ishga tushirilmoqda...</b>\n\n"
        "✅ Cache tozalandi\n"
        "✅ FSM tozalandi\n"
        "⏳ 3 soniyada restart bo'ladi..."
    )
    await cb.answer("🔄 Restart...")

    await asyncio.sleep(2)

    # Subprocess bilan qayta ishga tushirish (Windows da ishlaydi)
    import subprocess
    subprocess.Popen([sys.executable, "bot/main.py"])
    os._exit(0)


@router.callback_query(F.data == "adm:restart_confirm")
async def bot_restart_confirm(cb: CallbackQuery, user, state: FSMContext, **kw):
    if not await _check_admin(user):
        await cb.answer("❌", show_alert=True); return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, restart", callback_data="adm:restart"),
         InlineKeyboardButton(text="❌ Bekor", callback_data="adm:panel")],
    ])
    await cb.message.edit_text(
        "⚠️ <b>Botni restart qilmoqchimisiz?</b>\n\n"
        "Bu quyidagilarni bajaradi:\n"
        "• Barcha cache tozalanadi\n"
        "• FSM state tozalanadi\n"
        "• Bot 0 dan ishga tushadi\n\n"
        "Davom etasizmi?",
        reply_markup=kb
    )
    await cb.answer()


# ── PREMIUM BERISH ───────────────────────────────────
class GivePremiumSt(StatesGroup):
    tg_id = State()
    days  = State()


@router.callback_query(F.data == "adm:give_premium")
async def give_premium_start(cb: CallbackQuery, user, state: FSMContext, **kw):
    if not await _check_admin(user):
        await cb.answer("❌", show_alert=True); return
    await state.set_state(GivePremiumSt.tg_id)
    await cb.message.edit_text(
        "💎 <b>Premium berish</b>\n\n"
        "Foydalanuvchining Telegram ID sini yozing:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="❌ Bekor", callback_data="adm:panel")
        ]])
    )
    await cb.answer()


@router.message(GivePremiumSt.tg_id)
async def give_premium_tg_id(msg: Message, user, state: FSMContext, **kw):
    if not msg.text or not msg.text.strip().lstrip('-').isdigit():
        await msg.answer("❌ Faqat raqam kiriting!")
        return
    await state.update_data(target_tg_id=int(msg.text.strip()))
    await state.set_state(GivePremiumSt.days)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="30 kun", callback_data="pdays:30"),
         InlineKeyboardButton(text="60 kun", callback_data="pdays:60")],
        [InlineKeyboardButton(text="90 kun", callback_data="pdays:90"),
         InlineKeyboardButton(text="365 kun", callback_data="pdays:365")],
    ])
    await msg.answer("📅 Necha kun?", reply_markup=kb)


@router.callback_query(F.data.startswith("pdays:"), GivePremiumSt.days)
async def give_premium_days(cb: CallbackQuery, user, state: FSMContext, bot, **kw):
    if not await _check_admin(user):
        await cb.answer("❌", show_alert=True); return

    days = int(cb.data.split(":")[1])
    data = await state.get_data()
    target_tg_id = data.get('target_tg_id')
    await state.clear()

    from apps.users.models import User
    from django.utils import timezone
    from datetime import timedelta

    try:
        target = await sync_to_async(User.objects.get)(telegram_id=target_tg_id)
        target.is_premium = True
        target.premium_until = timezone.now() + timedelta(days=days)
        await sync_to_async(target.save)()

        # Cache tozalash — premium darhol ko'rinsin
        try:
            from bot.middlewares.auth import invalidate_user_cache
            invalidate_user_cache(target.telegram_id)
        except Exception:
            pass

        # Foydalanuvchiga xabar
        try:
            await bot.send_message(
                target_tg_id,
                f"🎉 <b>Tabriklaymiz!</b>\n\n"
                f"Sizga <b>{days} kunlik Premium</b> berildi!\n\n"
                f"✅ Cheksiz AI\n"
                f"✅ Barcha universitetlar\n"
                f"✅ Kirish foizi\n"
                f"✅ Shaxsiy o'qish rejasi"
            )
        except Exception:
            pass

        await cb.message.edit_text(
            f"✅ <b>{target.full_name}</b> ga\n"
            f"<b>{days} kunlik Premium</b> berildi!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🔙 Admin panel", callback_data="adm:panel")
            ]])
        )
    except User.DoesNotExist:
        await cb.message.edit_text(
            "❌ Foydalanuvchi topilmadi!\n"
            f"ID: {target_tg_id}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🔙 Admin panel", callback_data="adm:panel")
            ]])
        )
    await cb.answer()