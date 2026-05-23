from rest_framework import serializers
from .models import PremiumPlan, Payment, UserSubscription


class PremiumPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PremiumPlan
        fields = ['id', 'name', 'plan_type', 'price_usd', 'price_uzs',
                  'duration_days', 'features', 'description_uz', 'description_ru', 'description_en']


class PaymentSerializer(serializers.ModelSerializer):
    plan = PremiumPlanSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'plan', 'payment_method', 'status', 'amount',
                  'currency', 'order_id', 'created_at', 'completed_at']


class CreatePaymentSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=Payment.PaymentMethod.choices)


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = PremiumPlanSerializer(read_only=True)

    class Meta:
        model = UserSubscription
        fields = ['id', 'plan', 'started_at', 'expires_at', 'is_active', 'auto_renew']
