from django.contrib import admin
from .models import Notification, ExamDeadline

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notif_type', 'title', 'status', 'scheduled_at', 'sent_at']
    list_filter = ['notif_type', 'status']
    search_fields = ['user__telegram_id', 'title']

@admin.register(ExamDeadline)
class ExamDeadlineAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'deadline_date', 'reminder_days_before', 'is_notified']
    list_filter = ['is_notified']
