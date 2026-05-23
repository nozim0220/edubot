"""Education business logic."""
import logging
import random
from datetime import date
from typing import Optional, List
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache

from .models import (
    Subject, Question, Test, TestSession, TestQuestion,
    UserProgress, DailyChallenge, Certificate,
)
from apps.users.models import User

logger = logging.getLogger('apps')


class QuizService:
    """Handle quiz and test operations."""

    @staticmethod
    def get_random_questions(subject_id: int, count: int = 10, difficulty: str = None) -> List[Question]:
        """Get random questions for a subject."""
        qs = Question.objects.filter(subject_id=subject_id, is_active=True)
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        count = min(count, qs.count())
        return random.sample(list(qs), count)

    @staticmethod
    @transaction.atomic
    def start_test_session(user: User, test: Test) -> TestSession:
        """Start a new test session."""
        # Check if there's an existing in-progress session
        existing = TestSession.objects.filter(
            user=user, test=test, status=TestSession.Status.IN_PROGRESS
        ).first()
        if existing:
            return existing

        questions = test.questions.filter(is_active=True)
        session = TestSession.objects.create(
            user=user,
            test=test,
            total_questions=questions.count(),
            status=TestSession.Status.IN_PROGRESS,
        )
        logger.info(f"Test session started: user={user.pk}, test={test.pk}, session={session.pk}")
        return session

    @staticmethod
    @transaction.atomic
    def submit_answer(session: TestSession, question_id: int, answer: str) -> dict:
        """Submit an answer for a question."""
        try:
            question = Question.objects.get(pk=question_id, is_active=True)
        except Question.DoesNotExist:
            return {'error': 'Question not found'}

        is_correct = False
        if question.question_type == Question.QuestionType.MULTIPLE_CHOICE:
            is_correct = answer.upper() == question.correct_answer.upper()
        elif question.question_type == Question.QuestionType.TRUE_FALSE:
            is_correct = answer.lower() == question.correct_answer.lower()
        elif question.question_type == Question.QuestionType.SHORT_ANSWER:
            is_correct = answer.lower().strip() == question.answer_text.lower().strip()

        # Record answer
        session.answers[str(question_id)] = {
            'answer': answer,
            'correct': is_correct,
            'correct_answer': question.correct_answer,
        }

        if is_correct:
            session.correct_answers += 1
            xp = question.xp_reward
        else:
            xp = 0

        session.current_question_index += 1
        session.save(update_fields=['answers', 'correct_answers', 'current_question_index'])

        # Update question stats
        Question.objects.filter(pk=question_id).update(
            times_answered=question.times_answered + 1,
            times_correct=question.times_correct + (1 if is_correct else 0)
        )

        return {
            'is_correct': is_correct,
            'correct_answer': question.correct_answer,
            'explanation_uz': question.explanation_uz,
            'explanation_en': question.explanation_en,
            'xp_earned': xp,
        }

    @staticmethod
    @transaction.atomic
    def complete_session(session: TestSession) -> dict:
        """Complete a test session and calculate results."""
        session.status = TestSession.Status.COMPLETED
        session.completed_at = timezone.now()
        time_delta = session.completed_at - session.started_at
        session.time_taken_seconds = int(time_delta.total_seconds())
        session.score = session.percentage_score

        # Calculate XP
        xp_earned = session.correct_answers * settings.XP_PER_CORRECT_ANSWER
        if session.passed:
            xp_earned += settings.XP_PER_TEST_COMPLETION

        session.xp_earned = xp_earned
        session.save()

        # Update user XP and streak
        user = session.user
        user.add_xp(xp_earned)
        user.update_streak()

        # Update progress
        progress, _ = UserProgress.objects.get_or_create(
            user=user,
            subject=session.test.subject,
        )
        progress.tests_completed += 1
        progress.questions_answered += session.total_questions
        progress.correct_answers += session.correct_answers
        progress.total_xp += xp_earned
        if session.score > progress.best_score:
            progress.best_score = session.score
        progress.save()

        # Invalidate leaderboard cache
        # cache.delete_pattern("leaderboard:*")  # LocMemCache da yo'q
        try:
            cache.clear()
        except Exception:
            pass

        return {
            'score': session.score,
            'correct_answers': session.correct_answers,
            'total_questions': session.total_questions,
            'xp_earned': xp_earned,
            'passed': session.passed,
            'time_taken_seconds': session.time_taken_seconds,
        }

    @staticmethod
    def get_daily_challenge() -> Optional[DailyChallenge]:
        """Get today's daily challenge."""
        today = date.today()
        try:
            return DailyChallenge.objects.select_related('test__subject').get(date=today)
        except DailyChallenge.DoesNotExist:
            return None


class XPService:
    """Manage XP and level progression."""

    LEVEL_NAMES = {
        1: "🌱 Beginner", 2: "📖 Student", 3: "✏️ Learner",
        4: "🎯 Focused", 5: "⚡ Active", 6: "🔥 Dedicated",
        7: "💡 Thinker", 8: "🏆 Scholar", 9: "🎓 Expert",
        10: "⭐ Master", 15: "💎 Elite", 20: "👑 Legend",
    }

    @classmethod
    def get_level_name(cls, level: int) -> str:
        for lvl in sorted(cls.LEVEL_NAMES.keys(), reverse=True):
            if level >= lvl:
                return cls.LEVEL_NAMES[lvl]
        return "🌱 Beginner"

    @staticmethod
    def xp_for_next_level(current_level: int) -> int:
        thresholds = settings.LEVEL_THRESHOLDS
        next_level = current_level + 1
        if next_level in thresholds:
            return thresholds[next_level]
        return thresholds.get(current_level, 0) + 1000
