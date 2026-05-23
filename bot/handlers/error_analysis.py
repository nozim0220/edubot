"""Xato tahlili — qaysi savollarda ko'p xato qilgan."""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async

router = Router()
logger = logging.getLogger('bot')


@router.callback_query(F.data == "menu:errors")
async def error_analysis(cb: CallbackQuery, user, **kw):
    await cb.message.edit_text("🔍 Tahlil qilinmoqda...")

    stats = await sync_to_async(_get_error_stats)(user)

    if not stats:
        await cb.message.edit_text(
            "📊 <b>Xato tahlili</b>\n\n"
            "Hali yetarli test topshirilmagan.\n"
            "Ko'proq test ishlang!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="📚 Testlarga o'tish", callback_data="menu:education"),
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:main"),
            ]])
        )
        await cb.answer()
        return

    text = "📊 <b>Xato tahlili</b>\n\n"
    text += "Eng ko'p xato qilgan mavzular:\n\n"

    for i, s in enumerate(stats[:5], 1):
        bar = "🔴" * min(5, s['wrong']) + "🟢" * max(0, 5 - min(5, s['wrong']))
        text += (
            f"{i}. <b>{s['subject']}</b>\n"
            f"   {bar}\n"
            f"   ❌ {s['wrong']} xato / ✅ {s['correct']} to'g'ri\n\n"
        )

    text += "💡 Zaif fanlarni ko'proq mashq qiling!"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"📚 {stats[0]['subject']} ni mashq qilish",
            callback_data=f"edu:subject:{stats[0]['subject_id']}"
        )] if stats else [],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:main")],
    ])

    await cb.message.edit_text(text, reply_markup=kb)
    await cb.answer()


def _get_error_stats(user):
    try:
        from apps.education.models import UserProgress, Subject
        progresses = UserProgress.objects.filter(
            user=user, questions_answered__gt=0
        ).select_related('subject').order_by('-questions_answered')

        stats = []
        for p in progresses:
            wrong = p.questions_answered - p.correct_answers
            if wrong > 0:
                stats.append({
                    'subject': p.subject.name_uz,
                    'subject_id': p.subject.pk,
                    'wrong': wrong,
                    'correct': p.correct_answers,
                    'accuracy': p.accuracy_rate,
                })
        return sorted(stats, key=lambda x: x['wrong'], reverse=True)
    except Exception as e:
        logger.debug(f"Error stats: {e}")
        return []