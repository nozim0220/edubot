"""Universitetlar handler."""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async
from bot.keyboards.main import back_keyboard

router = Router()
logger = logging.getLogger('bot')


class UniState(StatesGroup):
    searching = State()


def _flag(c):
    flags = {'UZ':'🇺🇿','US':'🇺🇸','GB':'🇬🇧','DE':'🇩🇪','RU':'🇷🇺',
             'KR':'🇰🇷','TR':'🇹🇷','CN':'🇨🇳','JP':'🇯🇵','MY':'🇲🇾',
             'FR':'🇫🇷','IT':'🇮🇹','CA':'🇨🇦','AU':'🇦🇺'}
    return flags.get(c, '🌍')


@router.callback_query(F.data == "menu:universities")
async def uni_menu(cb: CallbackQuery, **kw):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 Qidirish",         callback_data="uni:search"),
            InlineKeyboardButton(text="⭐ Tavsiyalar",        callback_data="uni:recommend"),
        ],
        [
            InlineKeyboardButton(text="🌍 Mamlakat bo'yicha", callback_data="uni:country_menu"),
            InlineKeyboardButton(text="❤️ Saqlanganlar",      callback_data="uni:saved"),
        ],
        [InlineKeyboardButton(text="🏛 Kirish imkoniyatim",  callback_data="uni:my_chances")],
        [InlineKeyboardButton(text="🔙 Orqaga",              callback_data="menu:main")],
    ])
    await cb.message.edit_text("🏫 <b>Universitetlar</b>", reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data == "uni:search")
async def uni_search_start(cb: CallbackQuery, state: FSMContext, **kw):
    await state.set_state(UniState.searching)
    await cb.message.edit_text(
        "🔍 <b>Qidirish:</b>\nNom yoki shahar kiriting:",
        reply_markup=back_keyboard("menu:universities"),
    )
    await cb.answer()


@router.message(UniState.searching)
async def uni_search_do(msg: Message, state: FSMContext, **kw):
    await state.clear()
    from apps.universities.services import UniversitySearchService
    results = await sync_to_async(
        lambda: list(UniversitySearchService.search(query=msg.text.strip())[:12])
    )()
    if not results:
        await msg.answer("😔 Topilmadi.", reply_markup=back_keyboard("menu:universities"))
        return
    await _show_list(msg, results, f"🔍 {len(results)} ta natija")


@router.callback_query(F.data == "uni:country_menu")
async def country_menu(cb: CallbackQuery, **kw):
    countries = [
        ("🇺🇿 O'zbekiston","UZ"),("🇺🇸 USA","US"),("🇬🇧 UK","GB"),
        ("🇩🇪 Germaniya","DE"),("🇷🇺 Rossiya","RU"),("🇰🇷 Koreya","KR"),
        ("🇹🇷 Turkiya","TR"),("🇨🇳 Xitoy","CN"),("🇯🇵 Yaponiya","JP"),("🇲🇾 Malayziya","MY"),
    ]
    rows = []
    r = []
    for name, code in countries:
        r.append(InlineKeyboardButton(text=name, callback_data=f"uni:country:{code}"))
        if len(r) == 2: rows.append(r); r = []
    if r: rows.append(r)
    rows.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:universities")])
    await cb.message.edit_text(
        "🌍 <b>Mamlakat tanlang:</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )
    await cb.answer()


@router.callback_query(F.data.startswith("uni:country:"))
async def uni_by_country(cb: CallbackQuery, **kw):
    code = cb.data.split(":")[2]
    from apps.universities.services import UniversitySearchService
    results = await sync_to_async(
        lambda: list(UniversitySearchService.search(country=code)[:15])
    )()
    if not results:
        await cb.answer("Topilmadi!", show_alert=True); return
    cnames = {
        'UZ':"O'zbekiston",'US':"USA",'GB':"UK",'DE':"Germaniya",
        'RU':"Rossiya",'KR':"Koreya",'TR':"Turkiya",
        'CN':"Xitoy",'JP':"Yaponiya",'MY':"Malayziya"
    }
    await _show_list(
        cb.message, results,
        f"{_flag(code)} {cnames.get(code,code)} — {len(results)} ta",
        edit=True
    )
    await cb.answer()


async def _show_list(msg, unis, title: str, edit: bool = False):
    btns = []
    for u in unis:
        flag  = _flag(u.country)
        rank  = f"#{u.world_ranking}" if u.world_ranking else ""
        label = f"{flag} {u.name[:32]} {rank}".strip()
        btns.append([InlineKeyboardButton(text=label, callback_data=f"uni:detail:{u.pk}")])
    btns.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:universities")])
    kb = InlineKeyboardMarkup(inline_keyboard=btns)
    if edit:
        try:
            await msg.edit_text(f"🏫 <b>{title}</b>", reply_markup=kb)
        except Exception:
            await msg.answer(f"🏫 <b>{title}</b>", reply_markup=kb)
    else:
        await msg.answer(f"🏫 <b>{title}</b>", reply_markup=kb)


@router.callback_query(F.data.startswith("uni:detail:"))
async def uni_detail(cb: CallbackQuery, user, **kw):
    uid = int(cb.data.split(":")[2])
    from apps.universities.models import University, SavedUniversity, Faculty
    try:
        u        = await sync_to_async(University.objects.get)(pk=uid)
        is_saved = await sync_to_async(
            lambda: SavedUniversity.objects.filter(user=user, university=u).exists()
        )()
        faculties = await sync_to_async(
            lambda: list(Faculty.objects.filter(university=u, is_active=True)[:5])
        )()

        flag    = _flag(u.country)
        fee_usd = f"${u.tuition_fee_usd:,.0f}/yil" if u.tuition_fee_usd else ""
        fee_uzs = f"{int(u.tuition_fee_uzs):,} so'm/yil" if u.tuition_fee_uzs else ""
        fee_str = fee_usd or fee_uzs or "—"
        rank    = (f"#{u.world_ranking}" if u.world_ranking
                   else (f"#{u.national_ranking} (O'z)" if u.national_ranking else "—"))
        ielts   = str(u.required_ielts)      if u.required_ielts      else "—"
        sat_    = str(u.required_sat)         if u.required_sat         else "—"
        dtm     = str(u.dtm_passing_score)    if u.dtm_passing_score    else "—"
        schol   = "✅ Bor" if u.has_scholarships else "❌ Yo'q"
        desc    = u.description_uz or u.description_en or ""

        text = (
            f"{flag} <b>{u.name}</b>\n"
            f"📍 {u.city}, {u.get_country_display()}\n\n"
            f"🏆 Reyting: <b>{rank}</b>\n"
            f"💰 To'lov: <b>{fee_str}</b>\n"
            f"🎓 IELTS: <b>{ielts}</b>\n"
            f"📝 SAT: <b>{sat_}</b>\n"
            f"🇺🇿 DTM: <b>{dtm}</b>\n"
            f"🎁 Stipendiya: <b>{schol}</b>\n"
        )
        if u.scholarship_info:
            text += f"   ℹ️ {u.scholarship_info}\n"
        if u.application_deadline_fall:
            text += f"📅 Ariza muddati: <b>{u.application_deadline_fall}</b>\n"
        if u.website:
            text += f"🌐 <a href='{u.website}'>{u.website}</a>\n"
        if faculties:
            text += "\n🎓 <b>Fakultetlar:</b>\n"
            for f in faculties:
                fee_f = f"${f.tuition_fee_usd:,.0f}" if f.tuition_fee_usd else ""
                text += f"  • {f.name} {fee_f} | {f.duration_years}y | {f.language}\n"
        if desc:
            text += f"\n📖 {desc[:350]}{'...' if len(desc)>350 else ''}"

        save_txt = "💔 O'chirish" if is_saved else "❤️ Saqlash"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=save_txt,              callback_data=f"uni:save:{uid}"),
                InlineKeyboardButton(text="🎓 Barcha fakultetlar", callback_data=f"uni:faculties:{uid}"),
            ],
            [InlineKeyboardButton(text="🤖 AI tahlil",           callback_data=f"uni:ai:{uid}")],
            [InlineKeyboardButton(text="🏛 Kirish foizim",        callback_data=f"uni:chance:{uid}")],
            [InlineKeyboardButton(text="🔙 Orqaga",               callback_data="menu:universities")],
        ])
        await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"uni_detail: {e}")
        await cb.answer("Xato!", show_alert=True)
    await cb.answer()


@router.callback_query(F.data.startswith("uni:faculties:"))
async def all_faculties(cb: CallbackQuery, **kw):
    uid  = int(cb.data.split(":")[2])
    from apps.universities.models import Faculty
    facs = await sync_to_async(
        lambda: list(Faculty.objects.filter(university_id=uid, is_active=True))
    )()
    if not facs:
        await cb.answer("Fakultetlar ma'lumoti yo'q!", show_alert=True); return
    text = "🎓 <b>Barcha fakultetlar:</b>\n\n"
    for f in facs:
        fee = f"${f.tuition_fee_usd:,.0f}" if f.tuition_fee_usd else "—"
        text += f"• <b>{f.name}</b>\n  {f.degree} | {f.duration_years} yil | {fee} | {f.language}\n\n"
    await cb.message.edit_text(text, reply_markup=back_keyboard(f"uni:detail:{uid}"))
    await cb.answer()


@router.callback_query(F.data.startswith("uni:save:"))
async def toggle_save(cb: CallbackQuery, user, **kw):
    uid = int(cb.data.split(":")[2])
    from apps.universities.models import University, SavedUniversity
    u  = await sync_to_async(University.objects.get)(pk=uid)
    ex = await sync_to_async(
        lambda: SavedUniversity.objects.filter(user=user, university=u).first()
    )()
    if ex:
        await sync_to_async(ex.delete)()
        await cb.answer("❌ Saqlashdan o'chirildi")
    else:
        await sync_to_async(SavedUniversity.objects.create)(user=user, university=u)
        await cb.answer("❤️ Saqlandi!")
    await uni_detail(cb, user)


@router.callback_query(F.data.startswith("uni:ai:"))
async def uni_ai_analysis(cb: CallbackQuery, user, **kw):
    uid  = int(cb.data.split(":")[2])
    from apps.universities.models import University
    from bot.handlers.ai_assistant import _send_ai_quick
    u    = await sync_to_async(University.objects.get)(pk=uid)
    await cb.message.answer("🤖 AI tahlil qilmoqda...")
    certs    = await sync_to_async(user.get_certificates_summary)()
    cert_str = ", ".join(certs) if certs else "sertifikat kiritilmagan"
    prompt = (
        f"Talaba {u.name} universitetiga kirmoqchi.\n"
        f"Talabaning ball/sertifikatlari: {cert_str}\n"
        f"Universitet talablari: IELTS {u.required_ielts or '?'}, "
        f"SAT {u.required_sat or '?'}, DTM {u.dtm_passing_score or '?'}, "
        f"To'lov {u.tuition_fee_usd or '?'} USD/yil.\n"
        f"Stipendiya: {'bor — ' + u.scholarship_info if u.has_scholarships else 'yoq'}.\n"
        f"O'zbek tilida: 1) Kirish imkoniyati? 2) Nima tayyorlash kerak? "
        f"3) Qaysi stipendiyalar bor? (3-4 gap)"
    )
    tip = await _send_ai_quick(user, prompt)
    if tip:
        await cb.message.answer(
            f"🤖 <b>AI tahlili — {u.name}:</b>\n\n{tip}",
            reply_markup=back_keyboard(f"uni:detail:{uid}"),
        )
    await cb.answer()


@router.callback_query(F.data.startswith("uni:chance:"))
async def uni_my_chance(cb: CallbackQuery, user, **kw):
    from apps.universities.models import University

    is_premium = getattr(user, 'is_premium', False)

    if not is_premium:
        # 2 marta bepul, keyin premium
        from apps.users.models import User as UserModel
        u_obj  = await sync_to_async(UserModel.objects.get)(pk=user.pk)
        notes  = u_obj.notes or {}
        count  = notes.get('chance_count', 0)

        if count >= 2:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="💎 Premium ol — 29,900 so'm/oy",
                    callback_data="premium:buy"
                )],
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:universities")],
            ])
            await cb.message.edit_text(
                "🔒 <b>Bepul limit tugadi!</b>\n\n"
                "Kirish foizini <b>2 marta bepul</b> ko'rdingiz.\n\n"
                "💎 <b>Premium</b> oling — cheksiz foydalaning:\n"
                "✅ Barcha universitetlar AI tahlili\n"
                "✅ Shaxsiy maslahat\n\n"
                "💰 <b>29,900 so'm/oy</b>",
                reply_markup=kb
            )
            await cb.answer()
            return

        # Hisoblagichni oshirish
        notes['chance_count'] = count + 1
        u_obj.notes = notes
        await sync_to_async(u_obj.save)(update_fields=['notes'])

        left = 2 - (count + 1)
        if left > 0:
            await cb.answer(f"🎁 Yana {left} ta bepul qoldi", show_alert=False)
        else:
            await cb.answer("⚠️ Bu oxirgi bepul urinish!", show_alert=True)

    uid = int(cb.data.split(":")[2])
    u   = await sync_to_async(University.objects.get)(pk=uid)

    await cb.message.edit_text(
        f"🤖 <b>AI tahlil qilyapti...</b>\n\n"
        f"⏳ {u.name[:40]}\n"
        f"kirish ehtimoli hisoblanmoqda..."
    )

    result = await _ai_chance_analysis(user, u)
    try:
        await cb.message.edit_text(
            f"🏛 <b>{u.name}</b>\n\n{result}",
            reply_markup=back_keyboard(f"uni:detail:{uid}")
        )
    except Exception:
        await cb.message.answer(
            f"🏛 <b>{u.name}</b>\n\n{result}",
            reply_markup=back_keyboard(f"uni:detail:{uid}")
        )
    await cb.answer()


async def _ai_chance_analysis(user, u) -> str:
    try:
        from django.conf import settings as ds
        from openai import OpenAI
        import httpx, re

        key = getattr(ds, 'GROQ_API_KEY', '')
        if not key:
            return _manual_chance(user, u)

        ielts     = getattr(user, 'ielts_score', None)
        sat       = getattr(user, 'sat_score', None)
        dtm       = getattr(user, 'dtm_score', None)
        is_uz     = getattr(u, 'country', '') == 'UZ'
        ranking   = getattr(u, 'world_ranking', None) or getattr(u, 'national_ranking', None)
        has_schol = getattr(u, 'has_scholarships', False)
        country   = getattr(u, 'country', '')

        prompt = (
            f"Sen universitetga qabul boyicha ekspertsan. Haqiqiy tahlil ber.\n\n"
            f"Foydalanuvchi: IELTS={ielts or 'yoq'}, SAT={sat or 'yoq'}"
        )
        if is_uz:
            prompt += f", DTM={dtm or 'yoq'}"

        prompt += (
            f"\n\nUniversitet: {u.name}\n"
            f"Reyting: #{ranking or 'nomalum'}, Mamlakat: {country}\n"
            f"IELTS talabi: {getattr(u,'required_ielts',None) or 'yoq'}\n"
            f"SAT talabi: {getattr(u,'required_sat',None) or 'yoq'}\n"
        )
        if is_uz:
            prompt += f"DTM talabi: {getattr(u,'dtm_passing_score',None) or 'yoq'}\n"
        prompt += (
            f"Stipendiya: {'bor' if has_schol else 'yoq'}\n\n"
            f"Qoidalar: MIT/Harvard/Oxford = 5-20%, yaxshi O'zbek uni = 60-85%\n\n"
            f"Javob (HTML ishlatma, faqat matn):\n"
            f"Kirish ehtimoli: X%\n"
            f"[60%+ = yaxshi, 30-60% = orta, 30%- = past]\n\n"
            f"Afzalliklar:\n- ...\n\n"
            f"Kamchiliklar:\n- ...\n\n"
            f"Maslahat: ..."
        )

        client = OpenAI(
            api_key=key,
            base_url='https://api.groq.com/openai/v1',
            http_client=httpx.Client()
        )
        resp = client.chat.completions.create(
            model=getattr(ds, 'GROQ_MODEL', 'llama-3.3-70b-versatile'),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
        )
        text = resp.choices[0].message.content
        # HTML tozalash
        text = re.sub(r'<(?!/?(?:b|i|code))[^>]+>', '', text)

        # % va emoji moslashtirish
        match = re.search(r'(\d+)%', text)
        if match:
            pct = int(match.group(1))
            if pct >= 60:
                text = text.replace('🔴', '🟢').replace('🟡', '🟢')
            elif pct >= 30:
                text = re.sub(r'🟢(?!\s*60)', '🟡', text)
                text = text.replace('🔴', '🟡')
            else:
                text = text.replace('🟢', '🔴').replace('🟡', '🔴')

        return text.strip()
    except Exception as e:
        logger.error(f"AI chance: {e}")
        return _manual_chance(user, u)


def _manual_chance(user, u) -> str:
    is_uz = getattr(u, 'country', '') == 'UZ'
    score, total = 0, 0
    if getattr(u, 'required_ielts', None) and getattr(user, 'ielts_score', None):
        total += 30
        score += min(30, int(30 * min(float(user.ielts_score)/float(u.required_ielts), 1.2)))
    if getattr(u, 'required_sat', None) and getattr(user, 'sat_score', None):
        total += 30
        score += min(30, int(30 * min(user.sat_score/u.required_sat, 1.1)))
    if is_uz and getattr(u, 'dtm_passing_score', None) and getattr(user, 'dtm_score', None):
        total += 40
        score += min(40, int(40 * min(user.dtm_score/u.dtm_passing_score, 1.1)))
    if total == 0:
        return "Ball kiritilmagan.\nProfil → Tahrirlash"
    pct    = min(75, int(score/total*100))
    color  = "🟢" if pct >= 60 else "🟡" if pct >= 35 else "🔴"
    status = "Yaxshi" if pct >= 60 else "O'rta" if pct >= 35 else "Past"
    return f"Kirish ehtimoli: {color} <b>{pct}% — {status}</b>"


def _calc_chance(user, u) -> int:
    score, total = 0, 0
    if u.required_ielts:
        total += 30
        if user.ielts_score:
            score += min(30, int(30*min(float(user.ielts_score)/float(u.required_ielts), 1.3)))
    if u.required_sat:
        total += 30
        if user.sat_score:
            score += min(30, int(30*min(user.sat_score/u.required_sat, 1.2)))
    if u.dtm_passing_score and getattr(u,'country','') == 'UZ':
        total += 40
        if user.dtm_score:
            score += min(40, int(40*min(user.dtm_score/u.dtm_passing_score, 1.2)))
    if total == 0:
        return 0
    return min(85, int(score/total*100))


@router.callback_query(F.data == "uni:recommend")
async def uni_recommend(cb: CallbackQuery, user, **kw):
    from apps.universities.services import UniversitySearchService
    unis = await sync_to_async(UniversitySearchService.get_recommendations)(user)
    if not unis:
        await cb.answer("Tavsiyalar topilmadi!", show_alert=True); return
    await _show_list(cb.message, unis, "Siz uchun tavsiyalar", edit=True)
    await cb.answer()


@router.callback_query(F.data == "uni:saved")
async def uni_saved(cb: CallbackQuery, user, **kw):
    from apps.universities.models import SavedUniversity
    saved = await sync_to_async(
        lambda: list(SavedUniversity.objects.filter(user=user)
                    .select_related('university')[:15])
    )()
    if not saved:
        await cb.message.edit_text(
            "Saqlangan universitetlar yo'q.",
            reply_markup=back_keyboard("menu:universities"),
        )
        await cb.answer(); return
    await _show_list(cb.message, [s.university for s in saved], "Saqlanganlar", edit=True)
    await cb.answer()


@router.callback_query(F.data == "uni:my_chances")
async def all_my_chances(cb: CallbackQuery, user, **kw):
    from apps.universities.models import University

    is_premium = getattr(user, 'is_premium', False)
    if not is_premium:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="💎 Premium ol — 29,900 so'm/oy",
                callback_data="premium:buy"
            )],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:universities")],
        ])
        await cb.message.edit_text(
            "🔒 <b>Kirish foizi — Premium funksiya</b>\n\n"
            "💰 <b>29,900 so'm/oy</b>",
            reply_markup=kb
        )
        await cb.answer()
        return

    certs = await sync_to_async(user.get_certificates_summary)()
    if not certs:
        await cb.message.edit_text(
            "Ball kiritilmagan.\nProfil → Tahrirlash",
            reply_markup=back_keyboard("menu:universities"),
        )
        await cb.answer(); return

    await cb.message.edit_text("🤖 AI tahlil qilyapti...\n⏳ Hisoblanmoqda...")

    unis = await sync_to_async(
        lambda: list(University.objects.filter(is_active=True)
                    .order_by('world_ranking','national_ranking')[:10])
    )()

    import re
    results = []
    for u in unis:
        ai_text = await _ai_chance_analysis(user, u)
        match   = re.search(r'(\d+)%', ai_text)
        pct     = int(match.group(1)) if match else 0
        if pct > 0:
            results.append((u, pct))

    results = sorted(results, key=lambda x: x[1], reverse=True)[:8]

    if not results:
        await cb.message.edit_text(
            "Mos universitetlar topilmadi.",
            reply_markup=back_keyboard("menu:universities"),
        )
        await cb.answer(); return

    text = "🏛 <b>Kirish imkoniyatlari:</b>\n\n"
    btns = []
    for u, pct in results:
        color = "🟢" if pct >= 60 else "🟡" if pct >= 30 else "🔴"
        text += f"{color} {_flag(u.country)} {u.name[:35]} — <b>{pct}%</b>\n"
        btns.append([InlineKeyboardButton(
            text=f"{color} {u.name[:30]} — {pct}%",
            callback_data=f"uni:detail:{u.pk}"
        )])
    btns.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:universities")])
    await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=btns))
    await cb.answer()