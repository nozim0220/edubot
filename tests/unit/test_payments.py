"""Unit tests for payment services."""
import pytest
from django.test import TestCase
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestPaymentModels(TestCase):
    def setUp(self):
        from apps.users.models import User
        from apps.payments.models import PremiumPlan
        self.user = User.objects.create(telegram_id=123123123, first_name="Buyer")
        self.plan = PremiumPlan.objects.create(
            name="Monthly", plan_type="monthly",
            price_usd="9.99", price_uzs="125000",
            duration_days=30, is_active=True,
        )

    def test_generate_order_id(self):
        from apps.payments.services import generate_order_id
        oid = generate_order_id()
        self.assertTrue(oid.startswith("EDU-"))
        self.assertEqual(len(oid), 4 + 1 + 12)  # EDU- + 12 chars

    def test_payment_mark_completed(self):
        from apps.payments.models import Payment
        import uuid
        payment = Payment.objects.create(
            user=self.user, plan=self.plan,
            payment_method="click",
            amount="125000", currency="UZS",
            order_id=f"EDU-TEST{uuid.uuid4().hex[:8].upper()}",
        )
        payment.mark_completed()
        payment.refresh_from_db()
        self.assertEqual(payment.status, "completed")
        self.assertIsNotNone(payment.completed_at)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_premium)
        self.assertIsNotNone(self.user.premium_until)

    def test_subscription_created_on_payment(self):
        from apps.payments.models import Payment, UserSubscription
        import uuid
        payment = Payment.objects.create(
            user=self.user, plan=self.plan,
            payment_method="payme",
            amount="125000", currency="UZS",
            order_id=f"EDU-SUB{uuid.uuid4().hex[:8].upper()}",
        )
        payment.mark_completed()
        sub = UserSubscription.objects.get(payment=payment)
        self.assertTrue(sub.is_active)
        self.assertEqual(sub.plan, self.plan)
