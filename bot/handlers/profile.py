"""Profil + Shaxsiyat testi + Universitetga yo'naltirish."""
import logging
from aiogram import Router, F
from aiogram.types import (CallbackQuery, Message,
                            InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async
from bot.keyboards.main import back_keyboard, main_menu_keyboard

router = Router()
logger = logging.getLogger('bot')


class EditState(StatesGroup):
    value = State()


class PersonalityTest(StatesGroup):
    answering = State()
    pick_field   = State()
    pick_faculty = State()


# ── 15 TA SAVOL ──────────────────────────────────────
QUESTIONS = [
    {"text": "📚 <b>1/15</b> — Qaysi fanlarga qiziqasiz?",
     "opts": [("🧬 Biologiya va kimyo","bio"),("🔢 Matematika va iqtisodiyot","math"),
              ("💻 Informatika va dasturlash","it"),("⚖️ Biznes va huquq","biz")]},
    {"text": "🚀 <b>2/15</b> — Kelajakda nima bilan shug'ullanmoqchi?",
     "opts": [("🧠 Strategiyalar va muammolarni hal qilish","strategy"),
              ("🌿 Ekologik loyihalar","eco"),
              ("🎓 Odamlar bilan ishlash va ta'lim","edu"),
              ("💡 Yangi texnologiyalar yaratish","tech")]},
    {"text": "🏢 <b>3/15</b> — Qanday muhitda ishlashni istaysiz?",
     "opts": [("⚙️ Murakkab tizimlar va muammolar","system"),
              ("📊 Strategik va moliyaviy boshqaruv","finance"),
              ("❤️ Odamlarga yordam va adolat","social"),
              ("🔬 Innovatsiya va sog'liqni saqlash","health")]},
    {"text": "⭐ <b>4/15</b> — Eng katta motivatsiyangiz?",
     "opts": [("🚀 Yangi biznes va innovatsiyalar","innovation"),
              ("👥 Jamoa bilan yutuqlarga erishish","teamwork"),
              ("⚖️ Adolat va barqarorlik","justice"),
              ("🔬 Texnologiya va odamlar sog'lig'i","research")]},
    {"text": "🎮 <b>5/15</b> — Bo'sh vaqtingizda nima qilasiz?",
     "opts": [("📖 Bilim olish va boshqalarga yordam","learn"),
              ("💻 Texnologiya va tartibga solish","organize"),
              ("🎬 Kino, kitob yoki dam olish","leisure"),
              ("🌲 Tabiatda dam olish","nature")]},
    {"text": "🪞 <b>6/15</b> — O'zingizni qanday ta'riflaysiz?",
     "opts": [("💙 Mehribon va g'amxo'r","caring"),
              ("🔍 Sinchkov va diqqatli","detail"),
              ("🎨 Ijodkor va ilhomlantiruvchi","creative"),
              ("🏆 Strategik va qat'iyatli","strategic")]},
    {"text": "💪 <b>7/15</b> — Qiyinchiliklarni qanday yengasiz?",
     "opts": [("🧠 Tanqidiy fikrlash bilan","critical"),
              ("💡 Yangi yechimlar topib","adaptive"),
              ("🤝 Jamoa bilan birgalikda","collaborative"),
              ("🎯 Maqsad tasavvur qilib","visionary")]},
    {"text": "💼 <b>8/15</b> — Qanday ishlashni afzal ko'rasiz?",
     "opts": [("🖥️ Mustaqil va texnologiyalar bilan","independent"),
              ("👫 Jamoa bilan yaqin ishlash","team"),
              ("📋 Tizim va aniq qoidalar bilan","structured"),
              ("🎭 Ijodkorlik bilan yangiliklar","creative_work")]},
    {"text": "👑 <b>9/15</b> — Qanday lider bo'lasiz?",
     "opts": [("🤗 Qo'llab-quvvatlovchi","supportive"),
              ("📈 Maqsadga yo'naltirilgan","directive"),
              ("🎨 Kreativ va mas'uliyatli","creative_leader"),
              ("💬 Ishontiruvchi va qattiq qo'l","persuasive")]},
    {"text": "🌟 <b>10/15</b> — Sizni muvaffaqiyatga nima undaydi?",
     "opts": [("❤️ Boshqalarning hayotini yaxshilash","helping"),
              ("⚙️ Samarali mahsulotlar yaratish","building"),
              ("💰 Moliyaviy muammolarni hal qilish","financial"),
              ("🎯 Mazmunli narsalarni loyihalash","meaningful")]},
    {"text": "🛠️ <b>11/15</b> — Qaysi ko'nikma sizda eng kuchli?",
     "opts": [("🧠 Muammolarni hal qilish va mantiq","logic"),
              ("🗣️ Muloqot va ishontirish","communication"),
              ("🎨 Ijodkorlik va dizayn","design"),
              ("🤲 Odamlar bilan ishlash","people")]},
    {"text": "🎯 <b>12/15</b> — Qanday maqsadlar qo'yasiz?",
     "opts": [("🏢 Yirik kompaniyada yuqori lavozim","corporate"),
              ("🚀 O'z startapim","startup"),
              ("🎓 Ilmiy-tadqiqot karyerasi","academic"),
              ("🌍 Xalqaro tashkilotda ishlash","international")]},
    {"text": "🏫 <b>13/15</b> — Qanday ta'lim muhiti?",
     "opts": [("🌐 Xalqaro, ko'p madaniyatli","international_env"),
              ("🔬 Kuchli ilmiy-tadqiqot markazi","research_env"),
              ("💼 Amaliy va biznesga yo'naltirilgan","practical_env"),
              ("🤝 Kichik va do'stona jamoa","small_env")]},
    {"text": "🌈 <b>14/15</b> — Kelajakdagi soha:",
     "opts": [("💻 IT va sun'iy intellekt","IT"),
              ("💰 Moliya, iqtisodiyot, biznes","FINANCE"),
              ("⚙️ Muhandislik va energetika","ENGINEERING"),
              ("🏥 Tibbiyot va biologiya","MEDICINE"),
              ("⚖️ Huquq va diplomatiya","LAW"),
              ("🎨 Dizayn va arxitektura","DESIGN")]},
    {"text": "✅ <b>15/15</b> — Qaysi turdagi ta'limni afzal ko'rasiz?",
     "opts": [("📚 Ko'proq nazariya va ilmiy tadqiqot","theory"),
              ("🔧 Ko'proq amaliyot va loyihalar","practice"),
              ("🌍 Xalqaro dasturlar va almashinuv","exchange"),
              ("💼 Biznes va karyeraga yo'naltirilgan","career")]},
]

FACULTY_MAP = {
    "IT":          ["Kompyuter fanlari","Dasturiy injiniring","Kibexavfsizlik","Matematika va informatika","Sun'iy intellekt"],
    "FINANCE":     ["Moliya va bank ishi","Iqtisodiyot","Biznes boshqaruvi","Buxgalteriya","Marketing"],
    "ENGINEERING": ["Mexanik muhandislik","Elektr muhandisligi","Muhandislik","Kimyo muhandisligi","Energetika"],
    "MEDICINE":    ["Tibbiyot","Biologiya","Farmatsevtika","Stomatologiya","Veterinariya"],
    "LAW":         ["Huquq","Xalqaro munosabatlar","Davlat boshqaruvi","Diplomatiya","Kriminologiya"],
    "DESIGN":      ["Arxitektura va dizayn","Grafik dizayn","Badiiy ta'lim","Sanoat dizayni"],
}

UNI_MAP = {
    "IT":          ["MIT","Stanford","KAIST","INHA","WIUT","TUM","UTokyo","THU"],
    "FINANCE":     ["Harvard","Oxford","Cambridge","SNU","WIUT","Stanford"],
    "ENGINEERING": ["MIT","TUM","TTPU","UTokyo","KyotoU","METU","INHA","KAIST"],
    "MEDICINE":    ["Harvard","Oxford","UTokyo","SNU","KyotoU","Cambridge"],
    "LAW":         ["Harvard","Oxford","Cambridge","SNU","METU"],
    "DESIGN":      ["TUM","TTPU","Oxford","UTokyo"],
}

FLAGS = {'UZ':'🇺🇿','US':'🇺🇸','GB':'🇬🇧','DE':'🇩🇪','RU':'🇷🇺',
         'KR':'🇰🇷','TR':'🇹🇷','CN':'🇨🇳','JP':'🇯🇵','MY':'🇲🇾'}


def _ikb(*rows): return InlineKeyboardMarkup(inline_keyboard=list(rows))


async def _send_question(msg, q_idx: int, edit: bool = False):
    """Savol yuborish."""
    if q_idx >= len(QUESTIONS):
        return False
    q    = QUESTIONS[q_idx]
    rows = [[InlineKeyboardButton(text=label, callback_data=f"pt:{q_idx}:{value}")]
            for label, value in q['opts']]
    kb   = InlineKeyboardMarkup(inline_keyboard=rows)
    if edit:
        try:
            await msg.edit_text(q['text'], reply_markup=kb)
            return True
        except Exception:
            pass
    await msg.answer(q['text'], reply_markup=kb)
    return True


# ── PROFIL ───────────────────────────────────────────
@router.callback_query(F.data == "menu:profile")
async def profile_menu(cb: CallbackQuery, user, lang: str, **kw):
    certs     = await sync_to_async(user.get_certificates_summary)()
    cert_line = " | ".join(certs) if certs else "—"
    goal_map  = {'uzbekistan':"🇺🇿 O'zbekistonda",'abroad':"✈️ Chet elda",'both':"🌐 Ikkalasi"}
    text = (
        f"👤 <b>{user.full_name}</b>\n\n"
        f"⭐ XP: {user.xp_points} | 🏆 Lv.{user.level} | 🔥 {user.study_streak} kun\n"
        f"📱 {user.phone_number or '—'}\n"
        f"📍 {user.region or '—'} / {user.city or '—'}\n"
        f"🏫 {user.school or '—'} | {user.grade or '—'}\n"
        f"🎯 {goal_map.get(user.study_goal,'—')}\n"
        f"🎓 Orzu: {user.dream_university or '—'}\n"
        f"📜 {cert_line}"
    )
    kb = _ikb(
        [InlineKeyboardButton(text="✏️ Tahrirlash",              callback_data="profile:edit")],
        [InlineKeyboardButton(text="🧠 Shaxsiyat testi (15 savol)", callback_data="pt:start")],
        [InlineKeyboardButton(text="🏫 Menga mos universitetlar",  callback_data="uni:my_chances")],
        [InlineKeyboardButton(text="🔙 Orqaga",                   callback_data="menu:main")],
    )
    await cb.message.edit_text(text, reply_markup=kb)
    await cb.answer()


# ── SHAXSIYAT TESTI ──────────────────────────────────
@router.callback_query(F.data == "pt:start")
async def pt_start(cb: CallbackQuery, state: FSMContext, **kw):
    await state.clear()
    await state.set_state(PersonalityTest.answering)
    await state.update_data(q_idx=0, answers={})
    await cb.message.edit_text(
        "🧠 <b>Shaxsiyat testi</b>\n\n"
        "15 ta savol asosida sizga mos <b>fakultet va universitetlar</b> tavsiya qilinadi!\n\n"
        "To'g'ri javob yo'q — o'zingizga eng mos variantni tanlang ✅",
        reply_markup=_ikb(
            [InlineKeyboardButton(text="▶️ Boshlash", callback_data="pt:go:0")],
            [InlineKeyboardButton(text="🔙 Orqaga",   callback_data="menu:profile")],
        )
    )
    await cb.answer()


@router.callback_query(F.data == "pt:go:0")
async def pt_go(cb: CallbackQuery, state: FSMContext, **kw):
    await _send_question(cb.message, 0, edit=True)
    await cb.answer()


@router.callback_query(F.data.startswith("pt:"), PersonalityTest.answering)
async def pt_answer(cb: CallbackQuery, state: FSMContext, **kw):
    parts = cb.data.split(":")
    # pt:q_idx:value
    if len(parts) < 3:
        await cb.answer(); return

    try:
        q_idx = int(parts[1])
        value = parts[2]
    except (ValueError, IndexError):
        await cb.answer(); return

    # Javobni saqlash
    data    = await state.get_data()
    answers = data.get('answers', {})
    answers[str(q_idx)] = value
    next_q  = q_idx + 1
    await state.update_data(answers=answers, q_idx=next_q)

    if next_q < len(QUESTIONS):
        # Keyingi savol
        await _send_question(cb.message, next_q, edit=True)
    else:
        # Test tugadi — natija
        await state.set_state(PersonalityTest.pick_field)
        await _show_result(cb.message, state, answers)

    await cb.answer()


async def _show_result(msg, state: FSMContext, answers: dict):
    """Test natijasiga qarab soha tavsiya qilish."""
    # 14-savol (index 13) johi aniqlashtiradi
    field = answers.get('13', 'IT')
    await state.update_data(field=field)

    facs = FACULTY_MAP.get(field, ["Kompyuter fanlari","Matematika","Muhandislik"])

    rows = [[InlineKeyboardButton(
        text=f"🎓 {fac}",
        callback_data=f"pt_fac:{i}"
    )] for i, fac in enumerate(facs)]
    rows.append([InlineKeyboardButton(text="🔙 Qayta boshlash", callback_data="pt:start")])

    await state.update_data(fac_list=facs)
    await msg.edit_text(
        "✅ <b>15 ta savol tugadi!</b>\n\n"
        "Endi <b>fakultet</b> tanlang 👇",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("pt_fac:"), PersonalityTest.pick_field)
async def pt_pick_faculty(cb: CallbackQuery, state: FSMContext, user, **kw):
    fac_idx = int(cb.data.split(":")[1])
    data    = await state.get_data()
    facs    = data.get('fac_list', [])
    field   = data.get('field', 'IT')

    chosen = facs[fac_idx] if fac_idx < len(facs) else "Kompyuter fanlari"
    await state.clear()

    # Universitetlarni topish
    short_names = UNI_MAP.get(field, ["MIT","Oxford","TUM"])
    from apps.universities.models import University

    unis = await sync_to_async(
        lambda: list(University.objects.filter(
            short_name__in=short_names, is_active=True
        ).order_by('world_ranking', 'national_ranking')[:6])
    )()

    if not unis:
        unis = await sync_to_async(
            lambda: list(University.objects.filter(is_active=True, is_featured=True)[:6])
        )()

    # Profil yangilash
    await sync_to_async(user.__class__.objects.filter(pk=user.pk).update)(
        dream_university=chosen
    )

    text = (
        f"🎉 <b>Test natijasi!</b>\n\n"
        f"🎓 Tanlangan yo'nalish: <b>{chosen}</b>\n\n"
        f"🏫 <b>Sizga mos universitetlar:</b>\n"
    )

    btns = []
    for u in unis:
        flag = FLAGS.get(u.country, '🌍')
        rank = f"#{u.world_ranking}" if u.world_ranking else f"#{u.national_ranking}(O'z)" if u.national_ranking else ""
        fee  = f"${int(u.tuition_fee_usd):,}/yil" if u.tuition_fee_usd else (
               f"{int(u.tuition_fee_uzs or 0):,} so'm" if u.tuition_fee_uzs else "Arzon/Bepul")
        schol = " 🎁" if u.has_scholarships else ""
        text += f"\n{flag} <b>{u.name}</b> {rank}\n   💰 {fee}{schol}\n"
        btns.append([InlineKeyboardButton(
            text=f"{flag} {u.name[:38]}",
            callback_data=f"uni:detail:{u.pk}"
        )])

    btns.append([InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:main")])

    await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=btns))
    await cb.answer()


# ── PROFIL TAHRIRLASH ────────────────────────────────
@router.callback_query(F.data == "profile:edit")
async def profile_edit(cb: CallbackQuery, **kw):
    kb = _ikb(
        [InlineKeyboardButton(text="📱 Telefon",    callback_data="edit:phone"),
         InlineKeyboardButton(text="📍 Viloyat",    callback_data="edit:region")],
        [InlineKeyboardButton(text="🏙 Shahar",     callback_data="edit:city"),
         InlineKeyboardButton(text="🏫 Maktab",     callback_data="edit:school")],
        [InlineKeyboardButton(text="📊 IELTS",      callback_data="edit:ielts"),
         InlineKeyboardButton(text="📊 SAT",        callback_data="edit:sat")],
        [InlineKeyboardButton(text="📊 DTM",        callback_data="edit:dtm"),
         InlineKeyboardButton(text="🎓 Orzu univ.", callback_data="edit:dream")],
        [InlineKeyboardButton(text="🔙 Orqaga",     callback_data="menu:profile")],
    )
    await cb.message.edit_text("✏️ <b>Neni tahrirlash?</b>", reply_markup=kb)
    await cb.answer()


EDIT_FIELDS = {
    'phone':  ("📱 Yangi telefon raqam (+998...):", 'phone_number'),
    'region': ("📍 Viloyatni kiriting:",             'region'),
    'city':   ("🏙 Shaharni kiriting:",              'city'),
    'school': ("🏫 Maktab nomini kiriting:",         'school'),
    'ielts':  ("📊 IELTS ball kiriting (masalan: 7.5):", 'ielts_score'),
    'sat':    ("📊 SAT ball kiriting (masalan: 1400):",  'sat_score'),
    'dtm':    ("📊 DTM ball kiriting (masalan: 189):",   'dtm_score'),
    'dream':  ("🎓 Orzudagi universitetni kiriting:",    'dream_university'),
}


@router.callback_query(F.data.startswith("edit:"))
async def edit_field(cb: CallbackQuery, state: FSMContext, **kw):
    key = cb.data.split(":")[1]
    if key not in EDIT_FIELDS:
        await cb.answer(); return
    label, db_field = EDIT_FIELDS[key]
    await state.set_state(EditState.value)
    await state.update_data(db_field=db_field, field_key=key)
    await cb.message.edit_text(
        f"{label}",
        reply_markup=_ikb([InlineKeyboardButton(text="❌ Bekor", callback_data="profile:edit")])
    )
    await cb.answer()


@router.message(EditState.value)
async def edit_save(msg: Message, user, state: FSMContext, lang: str, **kw):
    data     = await state.get_data()
    db_field = data.get('db_field', '')
    value    = msg.text.strip()

    # Raqamli maydonlar
    if db_field == 'ielts_score':
        try: value = float(value)
        except ValueError:
            await msg.answer("❌ Noto'g'ri! IELTS uchun raqam kiriting (masalan: 7.5)")
            return
    elif db_field in ('sat_score', 'dtm_score'):
        try: value = int(value)
        except ValueError:
            await msg.answer("❌ Noto'g'ri! Raqam kiriting (masalan: 1400)")
            return

    await sync_to_async(user.__class__.objects.filter(pk=user.pk).update)(**{db_field: value})
    await state.clear()

    is_admin = bool(user.is_admin or user.is_staff)
    await msg.answer(
        f"✅ <b>Saqlandi!</b>",
        reply_markup=main_menu_keyboard(lang, is_admin=is_admin)
    )
