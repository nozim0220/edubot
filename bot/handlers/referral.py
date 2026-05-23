"""Referal tizimi."""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async

router = Router()
logger = logging.getLogger('bot')

REFERRAL_BONUS_XP    = 100   # Referal beruvchiga
REFERRAL_NEWUSER_XP  = 50    # Yangi foydalanuvchiga


@router.callback_query(F.data == "menu:referral")
async def referral_menu(cb: CallbackQuery, user, **kw):
    await _show_referral(cb.message, user, edit=True)
    await cb.answer()


@router.message(F.text == "👥 Referal")
async def referral_msg(msg: Message, user, **kw):
    await _show_referral(msg, user, edit=False)


async def _show_referral(msg, user, edit=False):
    tg_id    = user.telegram_id
    ref_link = f"https://t.me/ABTyordamchi0_bot?start=ref_{tg_id}"

    ref_count = await sync_to_async(
        lambda: __import__('apps.users.models', fromlist=['User']).User
        .objects.filter(referred_by_id=user.pk).count()
    )()

    text = (
        f"👥 <b>Referal tizimi</b>\n\n"
        f"Do'stlaringizni taklif qiling:\n\n"
        f"🔗 Sizning havolangiz:\n"
        f"<code>{ref_link}</code>\n\n"
        f"📊 Jalb qilganlar: <b>{ref_count} ta</b>\n\n"
        f"🎁 Mukofot:\n"
        f"• Har jalb qilgan uchun: <b>+{REFERRAL_BONUS_XP} XP</b>\n"
        f"• Yangi foydalanuvchi: <b>+{REFERRAL_NEWUSER_XP} XP</b>\n\n"
        f"💡 Havola orqali kelgan foydalanuvchi\n"
        f"botga /start bosganida XP beriladi!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📤 Do'stlarga yuborish",
            switch_inline_query=f"ABT bot orqali IELTS, SAT, DTM tayyorgarlik! {ref_link}"
        )],
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:main")],
    ])

    try:
        if edit:
            await msg.edit_text(text, reply_markup=kb)
        else:
            await msg.answer(text, reply_markup=kb)
    except Exception:
        await msg.answer(text, reply_markup=kb)


async def process_referral(new_user, ref_id: int, bot):
    """Yangi user referal orqali kelganda."""
    try:
        from apps.users.models import User
        referrer = await sync_to_async(User.objects.filter(telegram_id=ref_id).first)()
        if not referrer or referrer.pk == new_user.pk:
            return

        # Referrerni saqlash
        await sync_to_async(
            User.objects.filter(pk=new_user.pk).update
        )(referred_by_id=referrer.pk)

        # XP berish
        await sync_to_async(referrer.add_xp)(REFERRAL_BONUS_XP)
        await sync_to_async(new_user.add_xp)(REFERRAL_NEWUSER_XP)

        # Referrerni xabardor qilish
        try:
            await bot.send_message(
                referrer.telegram_id,
                f"🎉 <b>Yangi referal!</b>\n\n"
                f"Do'stingiz botga qo'shildi!\n"
                f"🎁 +{REFERRAL_BONUS_XP} XP qo'shildi!"
            )
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Referral: {e}")