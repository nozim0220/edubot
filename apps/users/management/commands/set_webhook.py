"""Set Telegram webhook."""
import asyncio
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Set Telegram webhook URL'

    def add_arguments(self, parser):
        parser.add_argument('--delete', action='store_true', help='Delete webhook')

    def handle(self, *args, **options):
        asyncio.run(self._run(options['delete']))

    async def _run(self, delete: bool):
        from aiogram import Bot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode

        bot = Bot(
            token=settings.TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        if delete:
            await bot.delete_webhook()
            self.stdout.write(self.style.SUCCESS('Webhook deleted.'))
        else:
            url = settings.WEBHOOK_URL
            if not url:
                self.stdout.write(self.style.ERROR('WEBHOOK_URL is not set in .env'))
                return
            await bot.set_webhook(
                url=url,
                secret_token=settings.TELEGRAM_WEBHOOK_SECRET,
            )
            info = await bot.get_webhook_info()
            self.stdout.write(self.style.SUCCESS(f'Webhook set: {info.url}'))
        await bot.session.close()
