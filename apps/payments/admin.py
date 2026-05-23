from django.contrib import admin
from .models import PremiumPlan, Payment, UserSubscription

@admin.register(PremiumPlan)
class PremiumPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price_usd', 'price_uzs', 'duration_days', 'is_active']
    list_editable = ['is_active']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'plan', 'payment_method', 'status', 'amount', 'currency', 'created_at']
    list_filter = ['status', 'payment_method']
    search_fields = ['order_id', 'user__telegram_id', 'transaction_id']
    readonly_fields = ['order_id', 'created_at', 'completed_at']

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'started_at', 'expires_at', 'is_active']
    list_filter = ['is_active', 'plan']
