"""Notification models for EduBot platform."""
from django.db import models
from apps.users.models import User


class Notification(models.Model):
    """System notifications."""

    class NotifType(models.TextChoices):
        STUDY_REMINDER = 'study_reminder', 'Study Reminder'
        EXAM_REMINDER = 'exam_reminder', 'Exam Reminder'
        DEADLINE_ALERT = 'deadline_alert', 'Deadline Alert'
        ACHIEVEMENT = 'achievement', 'Achievement'
        BROADCAST = 'broadcast', 'Broadcast'
        SYSTEM = 'system', 'System'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SENT = 'sent', 'Sent'
        FAILED = 'failed', 'Failed'
        READ = 'read', 'Read'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=30, choices=NotifType.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    scheduled_at = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['scheduled_at', 'status']),
        ]

    def __str__(self):
        return f"{self.notif_type} -> {self.user}"


class ExamDeadline(models.Model):
    """Track exam and university application deadlines."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_deadlines')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    deadline_date = models.DateField()
    reminder_days_before = models.PositiveSmallIntegerField(default=7)
    is_notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'exam_deadlines'
        ordering = ['deadline_date']

    def __str__(self):
        return f"{self.title} - {self.deadline_date}"
