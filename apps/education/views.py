"""Education views."""
import logging
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import Subject, Test, TestSession, UserProgress, Certificate
from .serializers import (
    SubjectSerializer, TestSerializer, TestSessionSerializer,
    SubmitAnswerSerializer, UserProgressSerializer, CertificateSerializer,
    QuestionSerializer, QuestionResultSerializer,
)
from .services import QuizService, XPService

logger = logging.getLogger('apps')


class SubjectListView(generics.ListAPIView):
    """List all active subjects."""
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Subject.objects.filter(is_active=True)

    @extend_schema(tags=['education'], summary="List all subjects")
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)


class TestListView(generics.ListAPIView):
    """List tests with filtering."""
    serializer_class = TestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['subject', 'test_type', 'is_premium']

    def get_queryset(self):
        qs = Test.objects.filter(is_active=True).select_related('subject')
        if not self.request.user.is_premium_active:
            qs = qs.filter(is_premium=False)
        return qs

    @extend_schema(tags=['education'], summary="List tests")
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)


@extend_schema(tags=['education'], summary="Start a test session")
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_test(request, test_id):
    """Start a test session."""
    try:
        test = Test.objects.get(pk=test_id, is_active=True)
    except Test.DoesNotExist:
        return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)

    if test.is_premium and not request.user.is_premium_active:
        return Response(
            {'error': 'This test requires a premium subscription'},
            status=status.HTTP_403_FORBIDDEN
        )

    session = QuizService.start_test_session(request.user, test)

    # Get questions for this session
    questions = test.questions.filter(is_active=True).order_by('testquestion__order')
    question_data = QuestionSerializer(questions, many=True).data

    return Response({
        'session': TestSessionSerializer(session).data,
        'questions': question_data,
    })


@extend_schema(tags=['education'], summary="Submit an answer")
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_answer(request):
    """Submit an answer for a question in a session."""
    serializer = SubmitAnswerSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        session = TestSession.objects.get(
            pk=serializer.validated_data['session_id'],
            user=request.user,
            status=TestSession.Status.IN_PROGRESS
        )
    except TestSession.DoesNotExist:
        return Response({'error': 'Session not found or not active'}, status=status.HTTP_404_NOT_FOUND)

    result = QuizService.submit_answer(
        session,
        serializer.validated_data['question_id'],
        serializer.validated_data['answer']
    )

    return Response({'success': True, 'result': result})


@extend_schema(tags=['education'], summary="Complete a test session")
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_test(request, session_id):
    """Complete a test session."""
    try:
        session = TestSession.objects.get(
            pk=session_id,
            user=request.user,
            status=TestSession.Status.IN_PROGRESS
        )
    except TestSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

    result = QuizService.complete_session(session)
    return Response({'success': True, 'result': result})


@extend_schema(tags=['education'], summary="Get my progress")
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_progress(request):
    """Get user's learning progress."""
    progress = UserProgress.objects.filter(
        user=request.user
    ).select_related('subject')

    level_name = XPService.get_level_name(request.user.level)
    xp_for_next = XPService.xp_for_next_level(request.user.level)

    return Response({
        'user': {
            'level': request.user.level,
            'level_name': level_name,
            'xp_points': request.user.xp_points,
            'xp_for_next_level': xp_for_next,
            'study_streak': request.user.study_streak,
        },
        'progress': UserProgressSerializer(progress, many=True).data,
    })


@extend_schema(tags=['education'], summary="Get daily challenge")
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def daily_challenge(request):
    """Get today's daily challenge."""
    challenge = QuizService.get_daily_challenge()
    if not challenge:
        return Response({'available': False, 'message': 'No daily challenge today'})

    return Response({
        'available': True,
        'challenge': {
            'id': challenge.id,
            'date': challenge.date,
            'test': TestSerializer(challenge.test).data,
            'bonus_xp': challenge.bonus_xp,
        }
    })


class MyCertificatesView(generics.ListAPIView):
    """List user's certificates."""
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Certificate.objects.filter(user=self.request.user)

    @extend_schema(tags=['education'], summary="My certificates")
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)


class MyTestHistoryView(generics.ListAPIView):
    """List user's test history."""
    serializer_class = TestSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TestSession.objects.filter(
            user=self.request.user,
            status=TestSession.Status.COMPLETED
        ).select_related('test__subject').order_by('-completed_at')

    @extend_schema(tags=['education'], summary="My test history")
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)
