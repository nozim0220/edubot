"""EduBot — Telegram Bot."""
import asyncio, logging, os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
import django; django.setup()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger('bot')


async def main():
    from aiogram import Bot, Dispatcher
    from aiogram.enums import ParseMode
    from aiogram.client.default import DefaultBotProperties
    from aiogram.fsm.storage.memory import MemoryStorage
    from django.conf import settings

    from bot.middlewares.auth import AuthMiddleware
    from bot.middlewares.subscription import SubscriptionMiddleware
    from bot.middlewares.throttle import ThrottlingMiddleware
    from bot.middlewares.i18n import I18nMiddleware
    from bot.handlers import (
        start, profile, education, universities,
        ai_assistant, payments, admin, games,
        settings as settings_handler
    )
    from bot.handlers import (
        premium, subscription, universities_premium,
        support, daily_task, leaderboard, referral,
        writing_check, error_analysis, exam_countdown, flashcard
    )

    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '').strip()
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN yo'q!"); return

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp  = Dispatcher(storage=MemoryStorage())

    for mw in [ThrottlingMiddleware(), AuthMiddleware(), I18nMiddleware(), SubscriptionMiddleware()]:
        dp.message.middleware(mw)
        dp.callback_query.middleware(mw)

    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(education.router)
    dp.include_router(premium.router)
    dp.include_router(subscription.router)
    dp.include_router(universities_premium.router)
    dp.include_router(universities.router)
    dp.include_router(ai_assistant.router)
    dp.include_router(payments.router)
    dp.include_router(admin.router)
    dp.include_router(games.router)
    dp.include_router(settings_handler.router)
    dp.include_router(support.router)
    dp.include_router(daily_task.router)
    dp.include_router(leaderboard.router)
    dp.include_router(referral.router)
    dp.include_router(writing_check.router)
    dp.include_router(error_analysis.router)
    dp.include_router(exam_countdown.router)
    dp.include_router(flashcard.router)

    await bot.delete_webhook(drop_pending_updates=True)
    me = await bot.get_me()
    print(f"\n✅ Bot ishga tushdi: @{me.username}\n")

    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            polling_timeout=3,
        )
    finally:
        await bot.session.close()


if __name__ == '__main__':
    while True:
        try:
            asyncio.run(main())
            break
        except KeyboardInterrupt:
            print("\n⛔ To'xtatildi.")
            break
        except Exception as e:
            logger.error(f"Bot xatosi: {e}")
            if "Router is already attached" in str(e):
                print("🔄 3 soniyada qayta ishga tushadi...")
                import time; time.sleep(3)
            else:
                print(f"🔄 3 soniyada qayta ishga tushadi...")
                import time; time.sleep(3)