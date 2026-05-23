"""Bot-level education service (async wrappers)."""
import logging
from asgiref.sync import sync_to_async

logger = logging.getLogger('bot')


async def get_subjects_async():
    """Get all active subjects."""
    from apps.education.models import Subject
    return await sync_to_async(list)(Subject.objects.filter(is_active=True))


async def get_tests_for_subject_async(subject_id: int, test_type: str = 'quiz'):
    """Get tests for a subject."""
    from apps.education.models import Test
    return await sync_to_async(
        lambda: list(Test.objects.filter(
            subject_id=subject_id, test_type=test_type, is_active=True
        ))
    )()


async def start_session_async(user, test):
    """Start test session."""
    from apps.education.services import QuizService
    return await sync_to_async(QuizService.start_test_session)(user, test)


async def submit_answer_async(session, question_id: int, answer: str) -> dict:
    """Submit answer."""
    from apps.education.services import QuizService
    return await sync_to_async(QuizService.submit_answer)(session, question_id, answer)


async def complete_session_async(session) -> dict:
    """Complete test session."""
    from apps.education.services import QuizService
    return await sync_to_async(QuizService.complete_session)(session)


async def get_user_progress_async(user, subject_id: int = None):
    """Get user progress."""
    from apps.education.models import UserProgress
    qs = UserProgress.objects.filter(user=user).select_related('subject')
    if subject_id:
        qs = qs.filter(subject_id=subject_id)
    return await sync_to_async(list)(qs)
