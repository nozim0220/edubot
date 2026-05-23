"""Payment processing services."""
import uuid
import logging
import stripe
from django.conf import settings
from django.utils import timezone

from .models import Payment, PremiumPlan, UserSubscription
from apps.users.models import User

logger = logging.getLogger('apps')
stripe.api_key = settings.STRIPE_SECRET_KEY


def generate_order_id() -> str:
    return f"EDU-{uuid.uuid4().hex[:12].upper()}"


class StripeService:
    """Stripe payment processing."""

    @staticmethod
    def create_payment_intent(user: User, plan: PremiumPlan) -> dict:
        intent = stripe.PaymentIntent.create(
            amount=int(plan.price_usd * 100),
            currency='usd',
            metadata={
                'user_id': str(user.pk),
                'plan_id': str(plan.pk),
                'telegram_id': str(user.telegram_id),
            }
        )
        order_id = generate_order_id()
        Payment.objects.create(
            user=user,
            plan=plan,
            payment_method=Payment.PaymentMethod.STRIPE,
            amount=plan.price_usd,
            currency='USD',
            order_id=order_id,
            provider_payment_id=intent.id,
        )
        return {'client_secret': intent.client_secret, 'order_id': order_id}

    @staticmethod
    def handle_webhook(payload: bytes, sig_header: str) -> bool:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            logger.error("Invalid Stripe webhook payload")
            return False
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid Stripe webhook signature")
            return False

        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            try:
                payment = Payment.objects.get(provider_payment_id=payment_intent.id)
                payment.transaction_id = payment_intent.id
                payment.mark_completed()
                logger.info(f"Stripe payment completed: {payment.order_id}")
            except Payment.DoesNotExist:
                logger.error(f"Payment not found for intent: {payment_intent.id}")
        return True


class ClickService:
    """Click.uz payment processing."""

    @staticmethod
    def prepare_url(user: User, plan: PremiumPlan) -> dict:
        order_id = generate_order_id()
        payment = Payment.objects.create(
            user=user,
            plan=plan,
            payment_method=Payment.PaymentMethod.CLICK,
            amount=plan.price_uzs,
            currency='UZS',
            order_id=order_id,
        )
        url = (
            f"https://my.click.uz/services/pay?"
            f"service_id={settings.CLICK_SERVICE_ID}"
            f"&merchant_id={settings.CLICK_MERCHANT_ID}"
            f"&amount={int(plan.price_uzs)}"
            f"&transaction_param={order_id}"
            f"&return_url=https://yourdomain.com/payment/success/"
        )
        return {'payment_url': url, 'order_id': order_id}

    @staticmethod
    def handle_callback(data: dict) -> bool:
        order_id = data.get('merchant_trans_id')
        click_trans_id = data.get('click_trans_id')
        error = data.get('error', 0)

        try:
            payment = Payment.objects.get(order_id=order_id)
            if int(error) == 0:
                payment.transaction_id = str(click_trans_id)
                payment.mark_completed()
                logger.info(f"Click payment completed: {order_id}")
                return True
            else:
                payment.status = Payment.Status.FAILED
                payment.error_message = f"Click error code: {error}"
                payment.save(update_fields=['status', 'error_message'])
                return False
        except Payment.DoesNotExist:
            logger.error(f"Payment not found: {order_id}")
            return False


class PaymeService:
    """Payme.uz payment processing."""

    @staticmethod
    def prepare_url(user: User, plan: PremiumPlan) -> dict:
        import base64
        order_id = generate_order_id()
        payment = Payment.objects.create(
            user=user,
            plan=plan,
            payment_method=Payment.PaymentMethod.PAYME,
            amount=plan.price_uzs,
            currency='UZS',
            order_id=order_id,
        )
        amount_tiyins = int(plan.price_uzs * 100)
        params = f"m={settings.PAYME_MERCHANT_ID};ac.order_id={order_id};a={amount_tiyins}"
        encoded = base64.b64encode(params.encode()).decode()
        url = f"https://checkout.paycom.uz/{encoded}"
        return {'payment_url': url, 'order_id': order_id}
