"""Telegram webhook endpoint for Django."""
import logging
import json
import hashlib
import hmac
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

logger = logging.getLogger('bot')


@csrf_exempt
def telegram_webhook(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    # Verify webhook secret
    secret = request.META.get('HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN', '')
    if settings.TELEGRAM_WEBHOOK_SECRET and secret != settings.TELEGRAM_WEBHOOK_SECRET:
        logger.warning(f"Invalid webhook secret: {secret[:10]}...")
        return HttpResponse(status=403)

    try:
        import asyncio
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

        from aiogram import Bot, Dispatcher
        from aiogram.types import Update
        from aiogram.enums import ParseMode
        from aiogram.client.default import DefaultBotProperties

        body = json.loads(request.body)
        logger.debug(f"Webhook received: {body.get('update_id')}")

        # Process update asynchronously
        asyncio.run(_process_update(body))
        return JsonResponse({'ok': True})
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


async def _process_update(body: dict):
    """Process incoming Telegram update."""
    from aiogram import Bot, Dispatcher
    from aiogram.types import Update
    from aiogram.enums import ParseMode
    from aiogram.client.default import DefaultBotProperties
    from aiogram.fsm.storage.redis import RedisStorage
    import redis.asyncio as aioredis
    from django.conf import settings

    from bot.middlewares.auth import AuthMiddleware
    from bot.middlewares.subscription import SubscriptionMiddleware
    from bot.middlewares.throttle import ThrottlingMiddleware
    from bot.middlewares.i18n import I18nMiddleware
    from bot.handlers import start, profile, education, universities, ai_assistant, payments, settings as settings_handler

    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    storage = RedisStorage(redis=redis_client)
    bot = Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)

    dp.message.middleware(ThrottlingMiddleware())
    dp.message.middleware(AuthMiddleware())
    dp.message.middleware(I18nMiddleware())
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    dp.callback_query.middleware(I18nMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(education.router)
    dp.include_router(universities.router)
    dp.include_router(ai_assistant.router)
    dp.include_router(payments.router)
    dp.include_router(settings_handler.router)

    update = Update(**body)
    await dp.feed_update(bot, update)
    await bot.session.close()
    await redis_client.aclose()
