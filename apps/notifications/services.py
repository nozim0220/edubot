"""Notification services."""
import logging
from django.utils import timezone
from .models import Notification, ExamDeadline
from apps.users.models import User

logger = logging.getLogger('apps')

class NotificationService:
    @staticmethod
    def create_notification(user, notif_type, title, message, scheduled_at=None, metadata=None):
        return Notification.objects.create(
            user=user, notif_type=notif_type, title=title, message=message,
            scheduled_at=scheduled_at or timezone.now(), metadata=metadata or {},
        )

    @staticmethod
    def get_pending_notifications():
        return Notification.objects.filter(
            status=Notification.Status.PENDING,
            scheduled_at__lte=timezone.now()
        ).select_related('user')
