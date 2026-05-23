"""Pytest configuration and shared fixtures."""
import os
import django
import pytest

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')


@pytest.fixture(scope='session')
def django_db_setup():
    pass


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def sample_user(db):
    from apps.users.models import User
    return User.objects.create(
        telegram_id=999999901,
        first_name="Test",
        last_name="User",
        telegram_username="testuser",
    )


@pytest.fixture
def premium_user(db):
    from apps.users.models import User
    from django.utils import timezone
    return User.objects.create(
        telegram_id=999999902,
        first_name="Premium",
        last_name="User",
        is_premium=True,
        premium_until=timezone.now() + timezone.timedelta(days=30),
    )


@pytest.fixture
def auth_client(api_client, sample_user):
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(sample_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    return api_client


@pytest.fixture
def sample_subject(db):
    from apps.education.models import Subject
    return Subject.objects.create(
        code='math', name_uz='Matematika',
        name_ru='Математика', name_en='Mathematics',
        emoji='🔢', is_active=True, order=1,
    )


@pytest.fixture
def sample_question(db, sample_subject):
    from apps.education.models import Question
    return Question.objects.create(
        subject=sample_subject,
        text_uz='2 + 2 = ?',
        option_a='3', option_b='4', option_c='5', option_d='6',
        correct_answer='B',
        xp_reward=10,
        is_active=True,
    )


@pytest.fixture
def sample_test(db, sample_subject, sample_question):
    from apps.education.models import Test, TestQuestion
    test = Test.objects.create(
        title_uz='Test 1', subject=sample_subject,
        test_type='quiz', passing_score=60, is_active=True,
    )
    TestQuestion.objects.create(test=test, question=sample_question, order=1)
    return test


@pytest.fixture
def sample_university(db):
    from apps.universities.models import University
    return University.objects.create(
        name="Test University",
        country="UZ", city="Tashkent",
        tuition_fee_usd="5000",
        has_scholarships=True,
        world_ranking=50,
        is_active=True,
    )
