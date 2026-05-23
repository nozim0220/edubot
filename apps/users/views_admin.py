"""Admin-only API views for analytics and management."""
import logging
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

logger = logging.getLogger('apps')


class IsAdminUser(permissions.BasePermission):
    """Only allow Django staff users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


@extend_schema(tags=['admin'], summary="Platform analytics dashboard")
@api_view(['GET'])
@permission_classes([IsAdminUser])
def analytics_dashboard(request):
    """Get platform analytics data."""
    from apps.users.models import User
    from apps.education.models import TestSession, UserProgress
    from apps.payments.models import Payment
    from apps.ai_assistant.models import AIUsageLog

    now = timezone.now()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # User stats
    total_users = User.objects.count()
    new_today = User.objects.filter(date_joined__date=today).count()
    new_week = User.objects.filter(date_joined__gte=week_ago).count()
    active_week = User.objects.filter(last_seen__gte=week_ago).count()
    premium_users = User.objects.filter(is_premium=True).count()
    banned_users = User.objects.filter(status='banned').count()

    # Test stats
    tests_today = TestSession.objects.filter(
        started_at__date=today, status='completed'
    ).count()
    tests_week = TestSession.objects.filter(
        started_at__gte=week_ago, status='completed'
    ).count()
    avg_score = TestSession.objects.filter(
        status='completed'
    ).aggregate(avg=Avg('score'))['avg'] or 0

    # Payment stats
    revenue_today = Payment.objects.filter(
        status='completed', completed_at__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    revenue_month = Payment.objects.filter(
        status='completed', completed_at__gte=month_ago
    ).aggregate(total=Sum('amount'))['total'] or 0

    # AI stats
    ai_requests_today = AIUsageLog.objects.filter(
        date=today
    ).aggregate(total=Sum('requests_count'))['total'] or 0

    return Response({
        'success': True,
        'analytics': {
            'users': {
                'total': total_users,
                'new_today': new_today,
                'new_week': new_week,
                'active_week': active_week,
                'premium': premium_users,
                'banned': banned_users,
            },
            'education': {
                'tests_completed_today': tests_today,
                'tests_completed_week': tests_week,
                'avg_score': round(avg_score, 1),
            },
            'revenue': {
                'today_usd': float(revenue_today),
                'month_usd': float(revenue_month),
            },
            'ai': {
                'requests_today': ai_requests_today,
            },
        }
    })


@extend_schema(tags=['admin'], summary="Send broadcast message")
@api_view(['POST'])
@permission_classes([IsAdminUser])
def send_broadcast(request):
    """Queue a broadcast message."""
    from apps.users.models import Broadcast
    from apps.notifications.tasks import send_broadcast_task

    title = request.data.get('title', '').strip()
    message = request.data.get('message', '').strip()
    audience = request.data.get('audience', Broadcast.TargetAudience.ALL)

    if not title or not message:
        return Response({'error': 'title and message are required'}, status=status.HTTP_400_BAD_REQUEST)

    broadcast = Broadcast.objects.create(
        title=title,
        message=message,
        target_audience=audience,
        status=Broadcast.Status.SCHEDULED,
        created_by=request.user,
    )
    send_broadcast_task.delay(broadcast.pk)
    return Response({'success': True, 'broadcast_id': broadcast.pk, 'status': 'queued'})


@extend_schema(tags=['admin'], summary="User growth chart data")
@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_growth(request):
    """Daily user registrations for the last 30 days."""
    from apps.users.models import User
    from django.db.models.functions import TruncDate

    data = (
        User.objects
        .filter(date_joined__gte=timezone.now() - timedelta(days=30))
        .annotate(date=TruncDate('date_joined'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    return Response({'success': True, 'data': list(data)})


@extend_schema(tags=['admin'], summary="Subject popularity stats")
@api_view(['GET'])
@permission_classes([IsAdminUser])
def subject_stats(request):
    """Stats by subject."""
    from apps.education.models import UserProgress, Subject
    data = []
    for subj in Subject.objects.filter(is_active=True):
        progress = UserProgress.objects.filter(subject=subj).aggregate(
            students=Count('user', distinct=True),
            tests=Sum('tests_completed'),
            avg_score=Avg('best_score'),
        )
        data.append({
            'subject': subj.name_en,
            'emoji': subj.emoji,
            'students': progress['students'] or 0,
            'tests_completed': progress['tests'] or 0,
            'avg_best_score': round(progress['avg_score'] or 0, 1),
        })
    return Response({'success': True, 'data': data})
