"""Celery tasks for notifications."""
import logging
from celery import shared_task
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger('apps')

@shared_task(bind=True, max_retries=3)
def send_telegram_message_task(self, telegram_id: int, message: str, parse_mode: str = 'HTML'):
    """Send a Telegram message to a user."""
    import asyncio
    import aiohttp
    async def _send():
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={
                'chat_id': telegram_id,
                'text': message,
                'parse_mode': parse_mode,
            }) as resp:
                return await resp.json()
    try:
        result = asyncio.run(_send())
        if not result.get('ok'):
            logger.warning(f"Failed to send message to {telegram_id}: {result}")
        return result
    except Exception as exc:
        logger.error(f"Error sending message to {telegram_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)

@shared_task
def send_broadcast_task(broadcast_id: int):
    """Send broadcast message to target users."""
    from apps.users.models import User, Broadcast
    try:
        broadcast = Broadcast.objects.get(pk=broadcast_id)
        broadcast.status = Broadcast.Status.RUNNING
        broadcast.save(update_fields=['status'])

        qs = User.objects.filter(is_active=True, status=User.Status.ACTIVE)
        if broadcast.target_audience == Broadcast.TargetAudience.PREMIUM:
            qs = qs.filter(is_premium=True)
        elif broadcast.target_audience == Broadcast.TargetAudience.FREE:
            qs = qs.filter(is_premium=False)
        elif broadcast.target_audience == Broadcast.TargetAudience.ACTIVE:
            week_ago = timezone.now() - timezone.timedelta(days=7)
            qs = qs.filter(last_seen__gte=week_ago)

        sent = 0
        failed = 0
        for user in qs.iterator():
            try:
                send_telegram_message_task.delay(user.telegram_id, broadcast.message)
                sent += 1
            except Exception:
                failed += 1

        broadcast.status = Broadcast.Status.COMPLETED
        broadcast.sent_count = sent
        broadcast.failed_count = failed
        broadcast.completed_at = timezone.now()
        broadcast.save(update_fields=['status', 'sent_count', 'failed_count', 'completed_at'])
        logger.info(f"Broadcast {broadcast_id} completed: {sent} sent, {failed} failed")
    except Exception as e:
        logger.error(f"Broadcast {broadcast_id} failed: {e}")

@shared_task
def send_study_reminders_task():
    """Send daily study reminders."""
    from apps.users.models import User
    now = timezone.localtime()
    users = User.objects.filter(
        remind_study=True, remind_time__isnull=False,
        status=User.Status.ACTIVE, is_active=True
    )
    for user in users:
        if user.remind_time and abs(
            (user.remind_time.hour * 60 + user.remind_time.minute) -
            (now.hour * 60 + now.minute)
        ) <= 5:
            msg = f"📚 Bugun o'qish vaqti! Streak: {user.study_streak} kun 🔥\nBotga qayting: /start"
            send_telegram_message_task.delay(user.telegram_id, msg)

@shared_task
def check_exam_deadlines_task():
    """Check and send exam deadline reminders."""
    from apps.notifications.models import ExamDeadline
    from datetime import date, timedelta
    today = date.today()
    deadlines = ExamDeadline.objects.filter(
        is_notified=False,
        deadline_date__lte=today + timedelta(days=7)
    ).select_related('user')
    for deadline in deadlines:
        days_left = (deadline.deadline_date - today).days
        msg = f"⏰ <b>{deadline.title}</b>\n📅 {days_left} kun qoldi!\n{deadline.description}"
        send_telegram_message_task.delay(deadline.user.telegram_id, msg)
        deadline.is_notified = True
        deadline.save(update_fields=['is_notified'])

@shared_task
def check_premium_expiry_task():
    """Notify users whose premium is expiring soon."""
    from apps.users.models import User
    from datetime import timedelta
    expiring_soon = User.objects.filter(
        is_premium=True,
        premium_until__lte=timezone.now() + timedelta(days=3),
        premium_until__gt=timezone.now()
    )
    for user in expiring_soon:
        days = (user.premium_until - timezone.now()).days
        msg = f"⚠️ Premium obunangiz {days} kun ichida tugaydi!\n💳 Yangilash: /premium"
        send_telegram_message_task.delay(user.telegram_id, msg)
