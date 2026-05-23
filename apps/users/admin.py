"""Admin configuration for users."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone
from .models import User, UserSession, BannedUser, Broadcast


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'telegram_id', 'full_name_display', 'telegram_username', 'status',
        'is_premium', 'level', 'xp_points', 'study_streak', 'language',
        'is_subscribed_to_channels', 'date_joined',
    ]
    list_filter = ['status', 'is_premium', 'language', 'is_subscribed_to_channels', 'is_staff']
    search_fields = ['telegram_id', 'telegram_username', 'first_name', 'last_name', 'phone_number']
    readonly_fields = ['date_joined', 'last_seen', 'xp_points', 'level', 'study_streak']
    ordering = ['-date_joined']

    fieldsets = (
        ('Telegram Info', {
            'fields': ('telegram_id', 'telegram_username', 'first_name', 'last_name', 'phone_number')
        }),
        ('Profile', {
            'fields': ('age', 'region', 'school', 'grade', 'study_language',
                       'interests', 'dream_university', 'exam_subjects', 'target_score')
        }),
        ('System', {
            'fields': ('language', 'status', 'is_subscribed_to_channels', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Premium', {
            'fields': ('is_premium', 'premium_until')
        }),
        ('Progress', {
            'fields': ('xp_points', 'level', 'study_streak', 'last_study_date')
        }),
        ('Notifications', {
            'fields': ('remind_study', 'remind_time', 'remind_exam')
        }),
        ('Timestamps', {
            'fields': ('date_joined', 'last_seen')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('telegram_id', 'first_name', 'last_name'),
        }),
    )

    def full_name_display(self, obj):
        return obj.full_name
    full_name_display.short_description = 'Full Name'

    actions = ['ban_users', 'unban_users', 'grant_premium', 'revoke_premium']

    def ban_users(self, request, queryset):
        for user in queryset:
            BannedUser.objects.get_or_create(
                user=user,
                defaults={'reason': 'Banned via admin', 'banned_by': request.user}
            )
            user.status = User.Status.BANNED
            user.save(update_fields=['status'])
        self.message_user(request, f"Banned {queryset.count()} users.")
    ban_users.short_description = "Ban selected users"

    def unban_users(self, request, queryset):
        BannedUser.objects.filter(user__in=queryset).delete()
        queryset.update(status=User.Status.ACTIVE)
        self.message_user(request, f"Unbanned {queryset.count()} users.")
    unban_users.short_description = "Unban selected users"

    def grant_premium(self, request, queryset):
        from datetime import timedelta
        queryset.update(
            is_premium=True,
            premium_until=timezone.now() + timedelta(days=30)
        )
        self.message_user(request, f"Granted premium to {queryset.count()} users.")
    grant_premium.short_description = "Grant 30-day premium"

    def revoke_premium(self, request, queryset):
        queryset.update(is_premium=False, premium_until=None)
        self.message_user(request, f"Revoked premium from {queryset.count()} users.")
    revoke_premium.short_description = "Revoke premium"


@admin.register(BannedUser)
class BannedUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'reason', 'banned_by', 'banned_at', 'expires_at', 'is_active']
    list_filter = ['banned_at']
    search_fields = ['user__telegram_id', 'user__telegram_username']
    readonly_fields = ['banned_at']


@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ['title', 'target_audience', 'status', 'sent_count', 'failed_count', 'created_at', 'scheduled_at']
    list_filter = ['status', 'target_audience']
    search_fields = ['title']
    readonly_fields = ['sent_count', 'failed_count', 'completed_at']

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    actions = ['send_now']

    def send_now(self, request, queryset):
        from apps.notifications.tasks import send_broadcast_task
        for broadcast in queryset.filter(status=Broadcast.Status.DRAFT):
            broadcast.status = Broadcast.Status.SCHEDULED
            broadcast.save(update_fields=['status'])
            send_broadcast_task.delay(broadcast.pk)
        self.message_user(request, "Broadcasts queued for sending.")
    send_now.short_description = "Send selected broadcasts now"


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'state', 'updated_at']
    search_fields = ['user__telegram_id']
    readonly_fields = ['updated_at']
