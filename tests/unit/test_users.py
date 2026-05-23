"""Unit tests for user models and services."""
import pytest
from django.test import TestCase
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestUserModel(TestCase):
    def setUp(self):
        from apps.users.models import User
        self.user = User.objects.create(
            telegram_id=123456789,
            first_name="Test",
            last_name="User",
        )

    def test_full_name(self):
        assert self.user.full_name == "Test User"

    def test_full_name_fallback(self):
        from apps.users.models import User
        u = User.objects.create(telegram_id=999)
        assert "999" in u.full_name

    def test_add_xp(self):
        self.user.add_xp(150)
        self.user.refresh_from_db()
        assert self.user.xp_points == 150
        assert self.user.level >= 2

    def test_is_premium_inactive_by_default(self):
        assert not self.user.is_premium_active

    def test_update_streak(self):
        from datetime import date, timedelta
        self.user.last_study_date = date.today() - timedelta(days=1)
        self.user.study_streak = 5
        self.user.save()
        self.user.update_streak()
        self.user.refresh_from_db()
        assert self.user.study_streak == 6

    def test_update_streak_reset(self):
        from datetime import date, timedelta
        self.user.last_study_date = date.today() - timedelta(days=3)
        self.user.study_streak = 10
        self.user.save()
        self.user.update_streak()
        self.user.refresh_from_db()
        assert self.user.study_streak == 1


@pytest.mark.django_db
class TestTelegramAuthService(TestCase):
    def test_get_or_create_new_user(self):
        from apps.users.services import TelegramAuthService
        data = {'id': 111222333, 'username': 'testbot', 'first_name': 'John', 'last_name': 'Doe'}
        user, created = TelegramAuthService.get_or_create_user(data)
        assert created is True
        assert user.telegram_id == 111222333
        assert user.telegram_username == 'testbot'

    def test_get_existing_user(self):
        from apps.users.services import TelegramAuthService
        data = {'id': 444555666, 'first_name': 'Jane', 'last_name': '', 'username': ''}
        user1, created1 = TelegramAuthService.get_or_create_user(data)
        user2, created2 = TelegramAuthService.get_or_create_user(data)
        assert created1 is True
        assert created2 is False
        assert user1.pk == user2.pk
