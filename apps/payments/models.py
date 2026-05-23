"""Payment models for EduBot platform."""
from django.db import models
from django.utils import timezone
from apps.users.models import User


class PremiumPlan(models.Model):
    """Premium subscription plans."""

    class PlanType(models.TextChoices):
        MONTHLY = 'monthly', 'Monthly'
        YEARLY = 'yearly', 'Yearly'
        LIFETIME = 'lifetime', 'Lifetime'

    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PlanType.choices)
    price_usd = models.DecimalField(max_digits=8, decimal_places=2)
    price_uzs = models.DecimalField(max_digits=12, decimal_places=2)
    duration_days = models.PositiveIntegerField(null=True, blank=True)
    description_uz = models.TextField(blank=True)
    description_ru = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    features = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'premium_plans'
        ordering = ['price_usd']

    def __str__(self):
        return f"{self.name} - ${self.price_usd}"


class Payment(models.Model):
    """Payment transactions."""

    class PaymentMethod(models.TextChoices):
        CLICK = 'click', 'Click'
        PAYME = 'payme', 'Payme'
        STRIPE = 'stripe', 'Stripe'
        TELEGRAM_STARS = 'telegram_stars', 'Telegram Stars'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(PremiumPlan, on_delete=models.SET_NULL, null=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=5, default='USD')

    # Transaction IDs from payment providers
    transaction_id = models.CharField(max_length=200, blank=True, null=True, unique=True)
    provider_payment_id = models.CharField(max_length=200, blank=True, null=True)
    order_id = models.CharField(max_length=100, unique=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['order_id']),
            models.Index(fields=['transaction_id']),
        ]

    def __str__(self):
        return f"Payment {self.order_id} - {self.user} ({self.status})"

    def mark_completed(self):
        """Mark payment as completed and activate premium."""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])

        # Activate premium
        if self.plan:
            subscription = UserSubscription.objects.create(
                user=self.user,
                plan=self.plan,
                payment=self,
                started_at=timezone.now(),
                expires_at=(
                    timezone.now() + timezone.timedelta(days=self.plan.duration_days)
                    if self.plan.duration_days else None
                )
            )
            self.user.is_premium = True
            self.user.premium_until = subscription.expires_at
            self.user.save(update_fields=['is_premium', 'premium_until'])


class UserSubscription(models.Model):
    """User premium subscription records."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(PremiumPlan, on_delete=models.SET_NULL, null=True)
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    started_at = models.DateTimeField()
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_subscriptions'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user} - {self.plan}"

    @property
    def is_expired(self):
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at
