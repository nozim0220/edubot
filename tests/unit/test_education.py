"""Unit tests for education services."""
import pytest
from django.test import TestCase


@pytest.mark.django_db
class TestQuizService(TestCase):
    def setUp(self):
        from apps.users.models import User
        from apps.education.models import Subject, Question, Test, TestQuestion
        self.user = User.objects.create(telegram_id=777888999, first_name="Student")
        self.subject = Subject.objects.create(
            code='math', name_uz='Matematika', name_ru='Математика', name_en='Mathematics', emoji='🔢'
        )
        self.test = Test.objects.create(
            title_uz='Test 1', subject=self.subject, test_type='quiz', passing_score=60
        )
        self.question = Question.objects.create(
            subject=self.subject, text_uz='2+2=?',
            option_a='3', option_b='4', option_c='5', option_d='6',
            correct_answer='B', xp_reward=10,
        )
        TestQuestion.objects.create(test=self.test, question=self.question, order=1)

    def test_start_test_session(self):
        from apps.education.services import QuizService
        session = QuizService.start_test_session(self.user, self.test)
        assert session.user == self.user
        assert session.test == self.test
        assert session.status == 'in_progress'

    def test_submit_correct_answer(self):
        from apps.education.services import QuizService
        session = QuizService.start_test_session(self.user, self.test)
        result = QuizService.submit_answer(session, self.question.pk, 'B')
        assert result['is_correct'] is True

    def test_submit_wrong_answer(self):
        from apps.education.services import QuizService
        session = QuizService.start_test_session(self.user, self.test)
        result = QuizService.submit_answer(session, self.question.pk, 'A')
        assert result['is_correct'] is False
        assert result['correct_answer'] == 'B'

    def test_complete_session(self):
        from apps.education.services import QuizService
        session = QuizService.start_test_session(self.user, self.test)
        QuizService.submit_answer(session, self.question.pk, 'B')
        session.refresh_from_db()
        result = QuizService.complete_session(session)
        assert result['correct_answers'] == 1
        assert result['score'] == 100
        assert result['passed'] is True
