from django.contrib import admin
from .models import AIChat, AIMessage, AIUsageLog

class AIMessageInline(admin.TabularInline):
    model = AIMessage
    extra = 0
    readonly_fields = ['role', 'content', 'tokens_used', 'created_at']
    can_delete = False

@admin.register(AIChat)
class AIChatAdmin(admin.ModelAdmin):
    list_display = ['user', 'chat_type', 'title', 'is_saved', 'total_tokens', 'created_at']
    list_filter = ['chat_type', 'is_saved']
    search_fields = ['user__telegram_id', 'title']
    inlines = [AIMessageInline]
    readonly_fields = ['total_tokens', 'created_at', 'updated_at']

@admin.register(AIUsageLog)
class AIUsageLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'requests_count', 'tokens_used']
    list_filter = ['date']
    date_hierarchy = 'date'
