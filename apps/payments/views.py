"""Payment views."""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import PremiumPlan, Payment, UserSubscription
from .serializers import (
    PremiumPlanSerializer, PaymentSerializer,
    CreatePaymentSerializer, UserSubscriptionSerializer,
)
from .services import StripeService, ClickService, PaymeService


class PremiumPlanListView(generics.ListAPIView):
    serializer_class = PremiumPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = PremiumPlan.objects.filter(is_active=True)

    @extend_schema(tags=['payments'], summary="List premium plans")
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)


@extend_schema(tags=['payments'], summary="Create a payment")
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_payment(request):
    serializer = CreatePaymentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        plan = PremiumPlan.objects.get(pk=serializer.validated_data['plan_id'], is_active=True)
    except PremiumPlan.DoesNotExist:
        return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)

    method = serializer.validated_data['payment_method']

    if method == Payment.PaymentMethod.STRIPE:
        result = StripeService.create_payment_intent(request.user, plan)
    elif method == Payment.PaymentMethod.CLICK:
        result = ClickService.prepare_url(request.user, plan)
    elif method == Payment.PaymentMethod.PAYME:
        result = PaymeService.prepare_url(request.user, plan)
    else:
        return Response({'error': 'Unsupported payment method'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'success': True, **result})


@extend_schema(tags=['payments'], summary="My payment history")
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_payments(request):
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')[:20]
    return Response({'success': True, 'payments': PaymentSerializer(payments, many=True).data})


@extend_schema(tags=['payments'], summary="My subscription")
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_subscription(request):
    try:
        sub = UserSubscription.objects.filter(
            user=request.user, is_active=True
        ).select_related('plan').latest('started_at')
        return Response({'success': True, 'subscription': UserSubscriptionSerializer(sub).data})
    except UserSubscription.DoesNotExist:
        return Response({'success': True, 'subscription': None})


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def stripe_webhook(request):
    """Stripe webhook handler."""
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    success = StripeService.handle_webhook(request.body, sig_header)
    if success:
        return Response({'status': 'ok'})
    return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def click_webhook(request):
    """Click.uz webhook handler."""
    success = ClickService.handle_callback(request.data)
    return Response({'error': 0 if success else 1, 'error_note': 'Success' if success else 'Failed'})
