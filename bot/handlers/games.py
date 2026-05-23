"""O'yinlar handler — ta'limiy o'yinlar."""
import logging, random
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async
from bot.keyboards.main import back_keyboard

router = Router()
logger = logging.getLogger('bot')


class GameState(StatesGroup):
    quiz_blitz  = State()
    true_false  = State()
    word_guess  = State()


# ── So'z topish o'yini ───────────────────────────────
WORD_GAMES = [
    {"word": "ALGEBRA", "hint": "Matematikaning bir bo'limi, Al-Xorazmiy kashf etgan", "category": "Matematika"},
    {"word": "OSMOSIS", "hint": "Suvning yarim o'tkazgich parda orqali o'tishi", "category": "Biologiya"},
    {"word": "PHOTON",  "hint": "Yorug'likning kvanti, massasiz zarracha",          "category": "Fizika"},
    {"word": "ISOTOPE", "hint": "Bir elementning turli massa sonli atomlari",         "category": "Kimyo"},
    {"word": "DYNASTY", "hint": "Bir sulolaga mansub hukmdorlar ketma-ketligi",      "category": "Tarix"},
    {"word": "SYNTAX",  "hint": "Dasturlash tilida kodning to'g'ri yozilish qoidasi", "category": "IT"},
    {"word": "GRAMMAR", "hint": "Tilning grammatika qoidalari tizimi",               "category": "Ingliz tili"},
    {"word": "THEOREM", "hint": "Isbotlangan matematik hukm",                        "category": "Matematika"},
    {"word": "NUCLEUS", "hint": "Hujayraning boshqaruv markazi",                     "category": "Biologiya"},
    {"word": "PROTON",  "hint": "Yadrodagi musbat zaryadli zarracha",                "category": "Fizika"},
    {"word": "CATALYST","hint": "Kimyoviy reaksiyani tezlashtiruvchi modda",         "category": "Kimyo"},
    {"word": "REPUBLIC","hint": "Saylangan rahbar boshqaradigan davlat boshqaruvi", "category": "Tarix"},
    {"word": "BINARY",  "hint": "Ikkilik sanoq sistemasi, 0 va 1 dan iborat",        "category": "IT"},
    {"word": "TENSE",   "hint": "Ingliz tilidagi zamon: o'tgan, hozirgi, kelasi",    "category": "Ingliz tili"},
    {"word": "INTEGRAL","hint": "Aniq integralni hisoblash operatsiyasi",            "category": "Matematika"},
]

# ── True/False o'yini ────────────────────────────────
TF_QUESTIONS = [
    {"q": "Yorug'lik vakuumda 3×10⁸ m/s tezlikda harakat qiladi.",      "ans": True,  "exp": "Ha, bu yorug'likning universal konstantasi"},
    {"q": "Suvning kimyoviy formulasi H₃O.",                              "ans": False, "exp": "Noto'g'ri! Suv H₂O — 2 vodorod + 1 kislorod"},
    {"q": "O'zbekiston 1991-yil 1-sentabrda mustaqillikka erishdi.",     "ans": True,  "exp": "Ha, 1991-yil 1-sentabr — Mustaqillik kuni"},
    {"q": "Python kompilyatsiya qilinadigan dasturlash tili.",           "ans": False, "exp": "Noto'g'ri! Python interpretatsiya qilinadigan til"},
    {"q": "Mitoxondriya — hujayra 'elektr stansiyasi'.",                 "ans": True,  "exp": "Ha, mitoxondriya ATP ishlab chiqaradi"},
    {"q": "IELTS maksimal bali 10.",                                     "ans": False, "exp": "Noto'g'ri! IELTS maksimal bali 9.0"},
    {"q": "Amir Temur 1336-yilda tug'ilgan.",                            "ans": True,  "exp": "Ha, Amir Temur Shahrisabzda 1336-yil tug'ilgan"},
    {"q": "(a+b)² = a² + b²",                                           "ans": False, "exp": "Noto'g'ri! (a+b)² = a² + 2ab + b²"},
    {"q": "DNK — dezoksiribonuklein kislota.",                           "ans": True,  "exp": "Ha, DNK = Deoxyribonucleic Acid"},
    {"q": "1 GB = 1000 MB",                                             "ans": False, "exp": "Noto'g'ri! 1 GB = 1024 MB (ikkilik sistema)"},
    {"q": "pH=7 neytral muhitni bildiradi.",                             "ans": True,  "exp": "Ha, pH 7 = neytral (distillangan suv)"},
    {"q": "Yer quyosh atrofida 24 soatda aylanadi.",                     "ans": False, "exp": "Noto'g'ri! Yer o'z o'qi atrofida 24 soatda, quyosh atrofida 365 kunda"},
    {"q": "Al-Xorazmiy algebra fanining asoschisi.",                     "ans": True,  "exp": "Ha, Muhammad al-Xorazmiy (783-850)"},
    {"q": "Sin(90°) = 0",                                               "ans": False, "exp": "Noto'g'ri! Sin(90°) = 1"},
    {"q": "Fotosintez xloroplastlarda amalga oshadi.",                   "ans": True,  "exp": "Ha, xloroplastlardagi xlorofill tufayli"},
]

# ── Quiz Blitz (30 soniya) ───────────────────────────
BLITZ_QS = [
    {"q": "2 + 2 × 2 = ?",               "opts": ["5","6","8","4"],  "ans": "6",  "exp": "Avval ko'paytma: 2×2=4, keyin qo'shish: 2+4=6"},
    {"q": "O'zbekiston poytaxti?",         "opts": ["Samarqand","Buxoro","Toshkent","Namangan"], "ans": "Toshkent", "exp": ""},
    {"q": "H₂O nima?",                    "opts": ["Tuz","Suv","Spirt","Kislorod"], "ans": "Suv",  "exp": ""},
    {"q": "Eng katta sayyora?",           "opts": ["Saturn","Mars","Yupiter","Neptun"], "ans": "Yupiter", "exp": ""},
    {"q": "log₁₀(100) = ?",              "opts": ["1","2","10","0.1"],"ans": "2",  "exp": "10² = 100"},
    {"q": "Python necha yili yaratilgan?", "opts": ["1985","1989","1991","1995"], "ans": "1991", "exp": "Guido van Rossum tomonidan"},
    {"q": "Qancha sonning 30% = 12?",    "opts": ["36","40","30","24"],"ans": "40", "exp": "x × 0.3 = 12 → x = 40"},
    {"q": "DNA necha zanjirdan iborat?",  "opts": ["1","2","3","4"],  "ans": "2",  "exp": "DNK ikki zanjirli spiral"},
    {"q": "IELTS qaysi mamlakat imtihoni?","opts": ["USA","UK","Avstraliya","Kanada"],"ans": "UK","exp": "British Council"},
    {"q": "Eng yengil element?",         "opts": ["Geliy","Litiy","Vodorod","Neon"],"ans": "Vodorod","exp": ""},
]


@router.callback_query(F.data == "menu:games")
async def games_menu(cb: CallbackQuery, **kw):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Quiz Blitz",      callback_data="game:blitz")],
        [InlineKeyboardButton(text="✅❌ True or False",  callback_data="game:tf")],
        [InlineKeyboardButton(text="🔤 So'z Topish",     callback_data="game:word")],
        [InlineKeyboardButton(text="🔙 Orqaga",          callback_data="menu:main")],
    ])
    await cb.message.edit_text(
        "🎮 <b>Ta'limiy o'yinlar</b>\n\n"
        "⚡ <b>Quiz Blitz</b> — tez savollar\n"
        "✅❌ <b>True or False</b> — rost yoki yolg'on\n"
        "🔤 <b>So'z Topish</b> — so'zni top\n\n"
        "O'yinlar orqali XP yig'ing! 🏆",
        reply_markup=kb,
    )
    await cb.answer()


# ── QUIZ BLITZ ───────────────────────────────────────
@router.callback_query(F.data == "game:blitz")
async def blitz_start(cb: CallbackQuery, state: FSMContext, **kw):
    questions = random.sample(BLITZ_QS, min(10, len(BLITZ_QS)))
    await state.set_state(GameState.quiz_blitz)
    await state.update_data(questions=questions, current=0, correct=0)
    await _send_blitz_q(cb.message, questions[0], 1, len(questions), edit=True)
    await cb.answer()


async def _send_blitz_q(msg, q: dict, num: int, total: int, edit: bool = False):
    opts = q['opts']
    random.shuffle(opts)
    btns = [InlineKeyboardButton(text=o, callback_data=f"blitz:ans:{o}") for o in opts]
    rows = [btns[:2], btns[2:]] if len(btns) >= 4 else [btns]
    kb   = InlineKeyboardMarkup(inline_keyboard=rows)
    text = f"⚡ <b>Blitz {num}/{total}</b>\n\n{q['q']}"
    if edit:
        try: await msg.edit_text(text, reply_markup=kb)
        except: await msg.answer(text, reply_markup=kb)
    else:
        await msg.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("blitz:ans:"), GameState.quiz_blitz)
async def blitz_answer(cb: CallbackQuery, user, state: FSMContext, **kw):
    answer = cb.data.split(":", 2)[2]
    data   = await state.get_data()
    qs     = data['questions']
    cur    = data['current']
    correct= data['correct']
    q      = qs[cur]
    is_ok  = answer == q['ans']
    if is_ok: correct += 1
    feedback = f"{'✅' if is_ok else '❌'} {q['ans']}"
    if q.get('exp'): feedback += f" — {q['exp']}"
    next_cur = cur + 1
    await state.update_data(current=next_cur, correct=correct)
    if next_cur >= len(qs):
        await state.clear()
        xp = correct * 3
        await sync_to_async(user.add_xp)(xp)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Qayta", callback_data="game:blitz")],
            [InlineKeyboardButton(text="🎮 O'yinlar", callback_data="menu:games")],
        ])
        await cb.message.edit_text(
            f"{feedback}\n\n"
            f"🏁 <b>Blitz tugadi!</b>\n"
            f"✅ {correct}/{len(qs)}  🎁 +{xp} XP",
            reply_markup=kb,
        )
    else:
        await cb.message.edit_text(feedback + "\n\n⏳...")
        await _send_blitz_q(cb.message, qs[next_cur], next_cur+1, len(qs))
    await cb.answer()


# ── TRUE OR FALSE ────────────────────────────────────
@router.callback_query(F.data == "game:tf")
async def tf_start(cb: CallbackQuery, state: FSMContext, **kw):
    qs = random.sample(TF_QUESTIONS, min(10, len(TF_QUESTIONS)))
    await state.set_state(GameState.true_false)
    await state.update_data(questions=qs, current=0, correct=0)
    await _send_tf_q(cb.message, qs[0], 1, len(qs), edit=True)
    await cb.answer()


async def _send_tf_q(msg, q: dict, num: int, total: int, edit: bool = False):
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ To'g'ri",  callback_data="tf:ans:true"),
        InlineKeyboardButton(text="❌ Noto'g'ri", callback_data="tf:ans:false"),
    ]])
    text = f"✅❌ <b>True/False {num}/{total}</b>\n\n{q['q']}"
    if edit:
        try: await msg.edit_text(text, reply_markup=kb)
        except: await msg.answer(text, reply_markup=kb)
    else:
        await msg.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("tf:ans:"), GameState.true_false)
async def tf_answer(cb: CallbackQuery, user, state: FSMContext, **kw):
    user_ans = cb.data.split(":")[2] == "true"
    data     = await state.get_data()
    qs, cur, correct = data['questions'], data['current'], data['correct']
    q        = qs[cur]
    is_ok    = user_ans == q['ans']
    if is_ok: correct += 1
    emoji    = "✅" if is_ok else "❌"
    feedback = f"{emoji} {'To\'g\'ri!' if is_ok else 'Noto\'g\'ri!'}\n💡 {q['exp']}"
    next_cur = cur + 1
    await state.update_data(current=next_cur, correct=correct)
    if next_cur >= len(qs):
        await state.clear()
        xp = correct * 4
        await sync_to_async(user.add_xp)(xp)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Qayta",    callback_data="game:tf")],
            [InlineKeyboardButton(text="🎮 O'yinlar", callback_data="menu:games")],
        ])
        await cb.message.edit_text(
            f"{feedback}\n\n🏁 <b>Tugadi!</b>\n✅ {correct}/{len(qs)}  🎁 +{xp} XP",
            reply_markup=kb,
        )
    else:
        await cb.message.edit_text(feedback)
        await _send_tf_q(cb.message, qs[next_cur], next_cur+1, len(qs))
    await cb.answer()


# ── SO'Z TOPISH ──────────────────────────────────────
@router.callback_query(F.data == "game:word")
async def word_start(cb: CallbackQuery, state: FSMContext, **kw):
    game = random.choice(WORD_GAMES)
    hidden = " ".join(["_"] * len(game["word"]))
    await state.set_state(GameState.word_guess)
    await state.update_data(word=game["word"], attempts=0, hint=game["hint"], category=game["category"])
    await cb.message.edit_text(
        f"🔤 <b>So'z Topish — {game['category']}</b>\n\n"
        f"💡 Maslahat: {game['hint']}\n\n"
        f"So'z: <code>{hidden}</code>\n"
        f"({len(game['word'])} harf)\n\n"
        f"Javobni yozing:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏳 Taslim", callback_data="word:surrender")]
        ]),
    )
    await cb.answer()


@router.message(GameState.word_guess)
async def word_guess(msg: Message, user, state: FSMContext, **kw):
    data    = await state.get_data()
    word    = data['word']
    attempt = data['attempts'] + 1
    guess   = msg.text.strip().upper()

    if guess == word:
        await state.clear()
        xp = max(5, 20 - attempt * 2)
        await sync_to_async(user.add_xp)(xp)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Yangi so'z",  callback_data="game:word")],
            [InlineKeyboardButton(text="🎮 O'yinlar",    callback_data="menu:games")],
        ])
        await msg.answer(
            f"🎉 <b>Barakalla! To'g'ri!</b> '{word}'\n\n"
            f"Urinishlar: {attempt}\n"
            f"🎁 +{xp} XP",
            reply_markup=kb,
        )
    elif attempt >= 5:
        await state.clear()
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Yangi so'z", callback_data="game:word")],
        ])
        await msg.answer(f"😔 5 urinish tugadi.\n✅ To'g'ri javob: <b>{word}</b>", reply_markup=kb)
    else:
        # Qisman ko'rsatish
        revealed = " ".join(c if c in guess or guess in word[:attempt] else "_" for c in word)
        await state.update_data(attempts=attempt)
        await msg.answer(
            f"❌ Noto'g'ri! ({5 - attempt} urinish qoldi)\n\n"
            f"So'z: <code>{revealed}</code>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏳 Taslim", callback_data="word:surrender")]
            ]),
        )


@router.callback_query(F.data == "word:surrender", GameState.word_guess)
async def word_surrender(cb: CallbackQuery, state: FSMContext, **kw):
    data = await state.get_data()
    await state.clear()
    await cb.message.edit_text(
        f"🏳 Taslim!\n✅ To'g'ri javob: <b>{data['word']}</b>",
        reply_markup=back_keyboard("menu:games"),
    )
    await cb.answer()
