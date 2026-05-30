"""Start handler — ReplyKeyboard menyu bilan."""
import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (Message, CallbackQuery,
                            InlineKeyboardMarkup, InlineKeyboardButton,
                            ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async
from django.conf import settings
from bot.keyboards.main import main_menu_keyboard, back_keyboard, inline_main_menu
from bot.middlewares.subscription import check_all_channels

router = Router()
logger = logging.getLogger('bot')

REGIONS = [
    "Toshkent sh.", "Toshkent vil.", "Samarqand", "Farg'ona",
    "Andijon", "Namangan", "Buxoro", "Xorazm", "Qashqadaryo",
    "Surxondaryo", "Sirdaryo", "Jizzax", "Navoiy", "Qoraqalpog'iston",
]


class OB(StatesGroup):
    phone  = State()
    age    = State()
    region = State()
    city   = State()
    school = State()
    grade  = State()
    goal   = State()
    dtm    = State()
    intl   = State()
    dream  = State()


def _ikb(*rows): return InlineKeyboardMarkup(inline_keyboard=list(rows))
def _btn(t, d):  return InlineKeyboardButton(text=t, callback_data=d)
def _skip(d):    return [InlineKeyboardButton(text="⏭ O'tkazish", callback_data=d)]


async def _show_main(msg_or_cb, user, lang: str):
    """Asosiy menyu — ReplyKeyboard pastda + xush kelibsiz xabari."""
    is_admin = bool(user.is_admin or user.is_staff)
    certs    = await sync_to_async(user.get_certificates_summary)()
    cert_line= " | ".join(certs) if certs else "—"
    text = (
        f"👋 <b>{user.full_name}</b>\n"
        f"⭐ XP: {user.xp_points}  🏆 Lv.{user.level}  🔥 {user.study_streak} kun\n"
        f"📜 {cert_line}\n\n"
        f"Quyidagi tugmalardan tanlang 👇"
    )
    kb = main_menu_keyboard(lang, is_admin=is_admin)
    if isinstance(msg_or_cb, CallbackQuery):
        await msg_or_cb.message.answer(text, reply_markup=kb)
        try:
            await msg_or_cb.message.delete()
        except Exception:
            pass
    else:
        await msg_or_cb.answer(text, reply_markup=kb)


# ── /start ───────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(msg: Message, user, lang: str, bot, state: FSMContext, **kw):
    if not user:
        await msg.answer("❌ Xato. /start qayta bosing.")
        return
    await state.clear()

    required = getattr(settings, 'REQUIRED_CHANNELS', [])
    if required:
        ok = await check_all_channels(bot, user.telegram_id, required)
        if not ok:
            from bot.keyboards.subscription import subscription_keyboard
            await msg.answer(
                "🔒 <b>Botdan foydalanish uchun obuna bo'ling!</b>",
                reply_markup=subscription_keyboard(required, lang),
            )
            return

    if not user.onboarding_done:
        await msg.answer(
            f"👋 Salom, <b>{user.first_name or 'Do\'stim'}</b>!\n\n"
            "🎓 <b>ABT Yordamchi</b> botiga xush kelibsiz!\n\n"
            "📌 Profilingizni to'ldiramiz — <b>1 daqiqa</b> ⏱"
        )
        await _ask_phone(msg, state)
    else:
        # Streak yangilash
        from bot.handlers.streak import update_streak, get_streak_emoji
    streak_data = await update_streak(user)

    # Referal tekshirish
    args = msg.text.split() if msg.text else []
    if len(args) > 1 and args[1].startswith('ref_'):
        try:
            ref_tg_id = int(args[1].replace('ref_', ''))
            from bot.handlers.referral import process_referral
            await process_referral(user, ref_tg_id, bot)
        except Exception:
            pass

    # Yangi kun bo'lsa streak xabari
    if streak_data['is_new_day'] and streak_data['streak'] > 1:
        emoji = get_streak_emoji(streak_data['streak'])
        await msg.answer(
            f"{emoji} <b>{streak_data['streak']} kunlik streak!</b>\n"
            f"🎁 +{streak_data['bonus_xp']} XP"
        )

    await _show_main(msg, user, lang)

@router.message(F.text == "🏫 Universitetlar")
async def btn_universities(msg: Message, user, lang: str, **kw):
    kb = _ikb(
        [_btn("🔍 Qidirish", "uni:search"), _btn("⭐ Tavsiyalar", "uni:recommend")],
        [_btn("🌍 Mamlakat bo'yicha", "uni:country_menu"), _btn("❤️ Saqlanganlar", "uni:saved")],
        [_btn("🏛 Kirish imkoniyatim", "uni:my_chances")],
    )
    await msg.answer("🏫 <b>Universitetlar</b>", reply_markup=kb)

@router.message(F.text == "🤖 AI Yordamchi")
async def btn_ai(msg: Message, **kw):
    kb = _ikb(
        [_btn("💬 Erkin suhbat",     "ai:general")],
        [_btn("📚 Uy ishi yordam",    "ai:homework")],
        [_btn("🔢 Matematik masala",  "ai:math")],
        [_btn("✍️ Grammatika",         "ai:grammar")],
        [_btn("🎯 Karyera maslahat",   "ai:career")],
        [_btn("📅 O'qish rejasi",      "ai:study_plan")],
    )
    await msg.answer("🤖 <b>AI Yordamchi</b>\n\nQaysi yordam kerak?", reply_markup=kb)

@router.message(F.text == "👤 Profil")
async def btn_profile(msg: Message, user, lang: str, **kw):
    certs    = await sync_to_async(user.get_certificates_summary)()
    cert_line= " | ".join(certs) if certs else "—"
    goal_map = {'uzbekistan':"🇺🇿 O'zbekistonda",'abroad':"✈️ Chet elda",'both':"🌐 Ikkalasi"}
    text = (
        f"👤 <b>{user.full_name}</b>\n\n"
        f"⭐ XP: {user.xp_points} | 🏆 Lv.{user.level} | 🔥 {user.study_streak} kun\n"
        f"📱 {user.phone_number or '—'}\n"
        f"📍 {user.region or '—'} / {user.city or '—'}\n"
        f"🏫 {user.school or '—'}\n"
        f"🎯 {goal_map.get(user.study_goal,'—')}\n"
        f"🎓 Orzu: {user.dream_university or '—'}\n"
        f"📜 {cert_line}"
    )
    kb = _ikb(
        [_btn("✏️ Tahrirlash",             "profile:edit")],
        [_btn("🧠 Shaxsiyat testi",        "pt:start")],
        [_btn("🏫 Menga mos universitetlar","uni:my_chances")],
    )
    await msg.answer(text, reply_markup=kb)


@router.message(F.text == "🎮 O'yinlar")
async def btn_games(msg: Message, **kw):
    kb = _ikb(
        [_btn("⚡ Quiz Blitz",     "game:blitz")],
        [_btn("✅❌ True or False", "game:tf")],
        [_btn("🔤 So'z Topish",    "game:word")],
    )
    await msg.answer("🎮 <b>Ta'limiy O'yinlar</b>", reply_markup=kb)

@router.message(F.text == "🏆 Reyting")
async def btn_leaderboard(msg: Message, user, **kw):
    from apps.users.services import UserService
    top    = await sync_to_async(UserService.get_leaderboard)(10)
    my_rank= await sync_to_async(UserService.get_user_rank)(user)
    text   = "🏆 <b>Top 10 reyting</b>\n\n"
    medals = ["🥇","🥈","🥉"]
    for i, u in enumerate(top):
        m    = medals[i] if i < 3 else f"{i+1}."
        name = (f"{u['first_name'] or ''} {u['last_name'] or ''}".strip()) or f"User#{u['id']}"
        text += f"{m} {name} — <b>{u['xp_points']}</b> XP\n"
    text += f"\n👤 Sizning o'rningiz: <b>#{my_rank}</b> ({user.xp_points} XP)"
    await msg.answer(text)

@router.message(F.text == "🔥 Kunlik vazifa")
async def btn_daily(msg: Message, user, state: FSMContext, **kw):
    from bot.handlers.daily_task import daily_menu
    await daily_menu(msg, user, state)



@router.message(F.text == "💎 Premium")
async def premium_msg(msg: Message, user, state: FSMContext, **kw):
    from bot.handlers.premium import premium_menu_msg
    await premium_menu_msg(msg, user)

@router.message(F.text == "⚙️ Sozlamalar")
async def btn_settings(msg: Message, user, lang: str, **kw):
    kb = _ikb(
        [_btn("🇺🇿 O'zbek", "lang:uz"), _btn("🇷🇺 Русский", "lang:ru"), _btn("🇬🇧 English", "lang:en")],
    )
    await msg.answer("⚙️ <b>Sozlamalar</b>\n\nTil tanlang:", reply_markup=kb)

@router.message(F.text == "🔐 Admin Panel")
async def btn_admin(msg: Message, user, **kw):
    if not (user.is_admin or user.is_staff):
        await msg.answer("❌ Sizda admin huquqi yo'q!")
        return
    from bot.handlers.admin import admin_panel
    await admin_panel(msg, user)


# ── ONBOARDING ───────────────────────────────────────
async def _ask_phone(msg, state):
    await state.set_state(OB.phone)
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True,
    )
    await msg.answer("📱 <b>1/9 — Telefon raqamingiz:</b>", reply_markup=kb)

@router.message(OB.phone, F.contact)
async def ob_phone(msg: Message, user, state, **kw):
    phone = msg.contact.phone_number
    if not phone.startswith('+'): phone = '+' + phone
    await sync_to_async(user.__class__.objects.filter(pk=user.pk).update)(phone_number=phone)
    await msg.answer("✅ Saqlandi!", reply_markup=ReplyKeyboardRemove())
    await _ask_age(msg, state)

@router.message(OB.phone, F.text)
async def ob_phone_text(msg: Message, user, state, **kw):
    t = msg.text.strip().replace(' ','').replace('-','')
    if t.lstrip('+').isdigit() and len(t.lstrip('+')) >= 9:
        phone = t if t.startswith('+') else '+' + t
        await sync_to_async(user.__class__.objects.filter(pk=user.pk).update)(phone_number=phone)
        await msg.answer("✅ Saqlandi!", reply_markup=ReplyKeyboardRemove())
        await _ask_age(msg, state)
    else:
        await msg.answer("❌ Format: +998901234567")

async def _ask_age(msg, state):
    await state.set_state(OB.age)
    rows = [[InlineKeyboardButton(text=str(a), callback_data=f"ob_age:{a}") for a in range(14+i*4, 18+i*4)] for i in range(2)]
    rows.append([InlineKeyboardButton(text="22+", callback_data="ob_age:22")])
    await msg.answer("🎂 <b>2/9 — Yoshingiz?</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))

@router.callback_query(F.data.startswith("ob_age:"), OB.age)
async def ob_age(cb: CallbackQuery, user, state, **kw):
    await sync_to_async(user.__class__.objects.filter(pk=user.pk).update)(age=int(cb.data.split(":")[1]))
    await cb.answer(); await _ask_region(cb.message, state)

async def _ask_region(msg, state):
    await state.set_state(OB.region)
    rows = []
    r = []
    for reg in REGIONS:
        r.append(InlineKeyboardButton(text=reg, callback_data=f"ob_reg:{reg}"))
        if len(r) == 2: rows.append(r); r = []
    if r: rows.append(r)
    await msg.answer("📍 <b>3/9 — Viloyat:</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))

@router.callback_query(F.data.startswith("ob_reg:"), OB.region)
async def ob_region(cb: CallbackQuery, user, state, **kw):
    await sync_to_async(user.__class__.objects.filter(pk=user.pk).update)(region=cb.data.split(":",1)[1])
    await cb.answer(); await _ask_city(cb.message, state)

async def _ask_city(msg, state):
    await state.set_state(OB.city)
    await msg.answer("🏙 <b>4/9 — Shahar/tuman:</b>")

@router.message(OB.city)
async def ob_city(msg: Message, user, state, **kw):
    await sync_to_async(user.__class__.objects.filter(pk=user.pk).update)(city=msg.text.strip())
    await _ask_school(msg, state)

async def _ask_school(msg, state):
    await state.set_state(OB.school)
    await msg.answer("🏫 <b>5/9 — Maktab/kollej:</b>",
        reply_markup=_ikb([InlineKeyboardButton(text="⏭ O'tkazish", callback_data="ob:skip_school")]))

@router.callback_query(F.data == "ob:skip_school", OB.school)
async def ob_skip_school(cb: CallbackQuery, state, **kw):
    await cb.answer(); await _ask_grade(cb.message, state)

@router.message(OB.school)
async def ob_school(msg: Message, user, state, **kw):
    await sync_to_async(user.__class__.objects.filter(pk=user.pk).update)(school=msg.text.strip())
    await _ask_grade(msg, state)

async def _ask_grade(msg, state):
    await state.set_state(OB.grade)
    grades = ["8","9","10","11","Bitiruvchi","Talaba","Boshqa"]
    rows = []
    r = []
    for g in grades:
        r.append(InlineKeyboardButton(text=g, callback_data=f"ob_grade:{g}"))
        if len(r) == 3: rows.append(r); r = []
    if r: rows.append(r)
    await msg.answer("📚 <b>6/9 — Sinf/bosqich:</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))

@router.callback_query(F.data.startswith("ob_grade:"), OB.grade)
async def ob_grade(cb: CallbackQuery, user, state, **kw):
    await sync_to_async(user.__class__.objects.filter(pk=user.pk).update)(grade=cb.data.split(":",1)[1])
    await cb.answer(); await _ask_goal(cb.message, state)

async def _ask_goal(msg, state):
    await state.set_state(OB.goal)
    await msg.answer("🎯 <b>7/9 — Qaerda o'qimoqchi?</b>",
        reply_markup=_ikb(
            [_btn("🇺🇿 O'zbekistonda", "ob_goal:uzbekistan")],
            [_btn("✈️ Chet elda",       "ob_goal:abroad")],
            [_btn("🌐 Ikkalasi ham",    "ob_goal:both")],
        ))

@router.callback_query(F.data.startswith("ob_goal:"), OB.goal)
async def ob_goal(cb: CallbackQuery, user, state, **kw):
    goal = cb.data.split(":")[1]
    await sync_to_async(user.__class__.objects.filter(pk=user.pk).update)(study_goal=goal)
    await cb.answer()
    if goal in ("uzbekistan","both"): await _ask_dtm(cb.message, state)
    else: await _ask_intl(cb.message, state)

async def _ask_dtm(msg, state):
    await state.set_state(OB.dtm)
    await msg.answer("📊 <b>8/9 — DTM/Milliy sertifikat ball:</b>\nMisol: <code>189</code>",
        reply_markup=_ikb(_skip("ob:skip_dtm")))

@router.callback_query(F.data == "ob:skip_dtm", OB.dtm)
async def ob_skip_dtm(cb: CallbackQuery, user, state, **kw):
    await cb.answer()
    goal = await sync_to_async(lambda: user.__class__.objects.values_list('study_goal',flat=True).get(pk=user.pk))()
    if goal in ("abroad","both"): await _ask_intl(cb.message, state)
    else: await _ask_dream(cb.message, state)

@router.message(OB.dtm)
async def ob_dtm(msg: Message, user, state, **kw):
    digits = ''.join(filter(str.isdigit, msg.text))
    if digits:
        field = 'nat_cert_score' if 'milliy' in msg.text.lower() else 'dtm_score'
        await sync_to_async(user.__class__.objects.filter(pk=user.pk).update)(**{field: int(digits)})
    goal = await sync_to_async(lambda: user.__class__.objects.values_list('study_goal',flat=True).get(pk=user.pk))()
    if goal in ("abroad","both"): await _ask_intl(msg, state)
    else: await _ask_dream(msg, state)

async def _ask_intl(msg, state):
    await state.set_state(OB.intl)
    await msg.answer("🌍 <b>8/9 — Xalqaro sertifikatlar:</b>\n<code>IELTS: 7.0</code>  <code>SAT: 1450</code>",
        reply_markup=_ikb(_skip("ob:skip_intl")))

@router.callback_query(F.data == "ob:skip_intl", OB.intl)
async def ob_skip_intl(cb: CallbackQuery, state, **kw):
    await cb.answer(); await _ask_dream(cb.message, state)

@router.message(OB.intl)
async def ob_intl(msg: Message, user, state, **kw):
    import re
    t = msg.text.lower()
    upd = {}
    m = re.search(r'ielts[:\s]+(\d+\.?\d*)', t)
    if m: upd['ielts_score'] = float(m.group(1))
    m = re.search(r'sat[:\s]+(\d+)', t)
    if m: upd['sat_score'] = int(m.group(1))
    if upd: await sync_to_async(user.__class__.objects.filter(pk=user.pk).update)(**upd)
    await _ask_dream(msg, state)

async def _ask_dream(msg, state):
    await state.set_state(OB.dream)
    await msg.answer("🎓 <b>9/9 — Orzudagi universitetingiz:</b>\nMisol: MIT, Oxford, INHA",
        reply_markup=_ikb(_skip("ob:skip_dream")))

@router.callback_query(F.data == "ob:skip_dream", OB.dream)
async def ob_skip_dream(cb: CallbackQuery, user, state, lang: str, **kw):
    await cb.answer(); await _finish(cb.message, user, state, lang)

@router.message(OB.dream)
async def ob_dream(msg: Message, user, state, lang: str, **kw):
    await sync_to_async(user.__class__.objects.filter(pk=user.pk).update)(dream_university=msg.text.strip())
    await _finish(msg, user, state, lang)

async def _finish(msg, user, state, lang):
    await state.clear()
    await sync_to_async(user.__class__.objects.filter(pk=user.pk).update)(onboarding_done=True)
    is_admin = bool(user.is_admin or user.is_staff)
    await msg.answer(
        "✅ <b>Profil to'ldirildi!</b>\n\nXush kelibsiz! 🚀\nQuyidagi tugmalardan foydalaning 👇",
        reply_markup=main_menu_keyboard(lang, is_admin=is_admin)
    )

# ── Kanal tekshirish ─────────────────────────────────
@router.callback_query(F.data == "check_subscription")
async def check_sub(cb: CallbackQuery, user, lang: str, bot, state, **kw):
    required = getattr(settings, 'REQUIRED_CHANNELS', [])
    ok = await check_all_channels(bot, user.telegram_id, required)
    if ok:
        await sync_to_async(user.__class__.objects.filter(pk=user.pk).update)(is_subscribed_to_channels=True)
        if not user.onboarding_done:
            await cb.message.edit_text("✅ Obuna tasdiqlandi!")
            await _ask_phone(cb.message, state)
        else:
            await cb.message.edit_text("✅ Obuna tasdiqlandi!")
            await _show_main(cb, user, lang)
    else:
        await cb.answer("❌ Hali obuna bo'lmadingiz!", show_alert=True)

# ── Til tanlash ──────────────────────────────────────
@router.callback_query(F.data.startswith("lang:"))
async def change_lang(cb: CallbackQuery, user, **kw):
    lang = cb.data.split(":")[1]
    await sync_to_async(user.__class__.objects.filter(pk=user.pk).update)(language=lang)
    names = {'uz':"O'zbek 🇺🇿", 'ru':"Русский 🇷🇺", 'en':"English 🇬🇧"}
    await cb.answer(f"✅ Til o'zgartirildi: {names.get(lang,'')}", show_alert=True)

# ── menu:main callback ───────────────────────────────
@router.callback_query(F.data == "menu:main")
async def menu_main_cb(cb: CallbackQuery, user, lang: str, **kw):
    await _show_main(cb, user, lang)
    await cb.answer()

# ── Reyting callback ─────────────────────────────────
@router.callback_query(F.data == "menu:leaderboard")
async def leaderboard_cb(cb: CallbackQuery, user, lang: str, **kw):
    from apps.users.services import UserService
    top     = await sync_to_async(UserService.get_leaderboard)(10)
    my_rank = await sync_to_async(UserService.get_user_rank)(user)
    text    = "🏆 <b>Top 10 reyting</b>\n\n"
    medals  = ["🥇","🥈","🥉"]
    for i, u in enumerate(top):
        m    = medals[i] if i < 3 else f"{i+1}."
        name = (f"{u['first_name'] or ''} {u['last_name'] or ''}".strip()) or f"User#{u['id']}"
        text += f"{m} {name} — <b>{u['xp_points']}</b> XP\n"
    text += f"\n👤 Sizning o'rningiz: <b>#{my_rank}</b> ({user.xp_points} XP)"
    await cb.message.answer(text, reply_markup=back_keyboard("menu:main", lang))
    await cb.answer()


@router.callback_query(F.data == "adm:panel")
async def adm_panel_start(cb: CallbackQuery, user, **kw):
    """Admin panel callback — start routerdan (filtersiz)."""
    if not (user and (user.is_admin or user.is_staff)):
        await cb.answer("❌ Admin huquqi yo'q!", show_alert=True)
        return
    from bot.handlers.admin import _show_panel
    await _show_panel(cb.message, edit=True)
    await cb.answer()


@router.message(F.text == "🆘 Yordam")
async def btn_support(msg: Message, user, state: FSMContext, **kw):
    from bot.handlers.support import support_menu
    await support_menu(msg, user, state)


@router.message(F.text == "👥 Referal")
async def btn_referral(msg: Message, user, **kw):
    from bot.handlers.referral import referral_msg
    await referral_msg(msg, user)


# ── GURUHGA QO'SHISH ──────────────────────────────────
@router.message(F.new_chat_members)
async def new_member_joined(msg: Message, bot, **kw):
    """Guruhga yangi a'zo qo'shilganda — qo'shgan odamga XP."""
    from apps.users.models import User
    from asgiref.sync import sync_to_async

    # Kim qo'shdi
    adder_id = msg.from_user.id if msg.from_user else None
    if not adder_id:
        return

    new_members = msg.new_chat_members or []
    # Botni qo'shishdan o'tkazib yuborish
    real_new = [m for m in new_members if not m.is_bot]
    if not real_new:
        return

    try:
        adder = await sync_to_async(User.objects.filter(telegram_id=adder_id).first)()
        if not adder:
            return

        xp_per_member = 30
        total_xp = xp_per_member * len(real_new)
        await sync_to_async(adder.add_xp)(total_xp)

        names = ", ".join(m.first_name or m.username or "?" for m in real_new)
        await bot.send_message(
            adder_id,
            f"🎉 <b>Rahmat!</b>\n\n"
            f"Guruhga {names} ni qo'shganingiz uchun\n"
            f"🎁 +{total_xp} XP qo'shildi!"
        )
    except Exception as e:
        pass


@router.message(F.text == "✍️ Writing")
async def btn_writing(msg: Message, user, **kw):
    from bot.handlers.writing_check import writing_menu
    await writing_menu(msg, user)


@router.message(F.text == "🃏 Flashcard")
async def btn_flashcard(msg: Message, user, **kw):
    from bot.handlers.flashcard import flashcard_menu
    from aiogram.types import CallbackQuery
    class FakeCb:
        message = msg
        async def answer(self): pass
    cb = FakeCb()
    cb.message = msg
    from aiogram.types import InlineKeyboardMarkup
    # To'g'ridan answer
    from bot.handlers.flashcard import FLASHCARDS, _get_flashcard_stats
    from asgiref.sync import sync_to_async
    stats = await sync_to_async(_get_flashcard_stats)(user)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [__import__('aiogram.types', fromlist=['InlineKeyboardButton']).InlineKeyboardButton(
            text="▶️ Boshlash", callback_data="fc:start:0")],
        [__import__('aiogram.types', fromlist=['InlineKeyboardButton']).InlineKeyboardButton(
            text="🏠 Menyu", callback_data="menu:main")],
    ])
    await msg.answer(
        f"🃏 <b>Flashcard</b>\n\n"
        f"O'rganilgan: {stats.get('known',0)}/{len(FLASHCARDS)}\n\n"
        f"Boshlash uchun tugmani bosing!",
        reply_markup=kb
    )


@router.message(F.text == "⏰ Imtihon sana")
async def btn_countdown(msg: Message, user, state: FSMContext, **kw):
    from bot.handlers.exam_countdown import _show_countdown
    await _show_countdown(msg, user, edit=False)


@router.message(F.text == "📊 Xato tahlili")
async def btn_errors(msg: Message, user, **kw):
    from bot.handlers.error_analysis import _get_error_stats
    from asgiref.sync import sync_to_async
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    stats = await sync_to_async(_get_error_stats)(user)
    if not stats:
        await msg.answer("Hali yetarli test topshirilmagan.")
        return
    text = "📊 <b>Xato tahlili</b>\n\n"
    for i, s in enumerate(stats[:5], 1):
        bar = "🔴" * min(5, s['wrong']) + "🟢" * max(0, 5 - min(5, s['wrong']))
        text += f"{i}. <b>{s['subject']}</b>\n   {bar} ❌{s['wrong']} ✅{s['correct']}\n"
    await msg.answer(text)