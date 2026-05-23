"""Unit tests for AI assistant."""
import pytest
from django.test import TestCase
from unittest.mock import patch, MagicMock
from datetime import date


@pytest.mark.django_db
class TestAIUsageLimit(TestCase):
    def setUp(self):
        from apps.users.models import User
        self.free_user = User.objects.create(telegram_id=555001, first_name="Free")
        self.premium_user = User.objects.create(
            telegram_id=555002, first_name="Premium",
            is_premium=True,
        )

    def test_free_user_limit(self):
        from apps.ai_assistant.services import AIService
        from django.conf import settings
        service = AIService()
        remaining, limit = service._check_usage_limit(self.free_user)
        self.assertEqual(limit, settings.AI_DAILY_FREE_LIMIT)
        self.assertEqual(remaining, settings.AI_DAILY_FREE_LIMIT)

    def test_premium_user_higher_limit(self):
        from apps.ai_assistant.services import AIService
        from django.conf import settings
        service = AIService()
        remaining, limit = service._check_usage_limit(self.premium_user)
        self.assertEqual(limit, settings.AI_DAILY_PREMIUM_LIMIT)

    def test_usage_decrements(self):
        from apps.ai_assistant.models import AIUsageLog
        from apps.ai_assistant.services import AIService
        from django.conf import settings
        AIUsageLog.objects.create(
            user=self.free_user, date=date.today(), requests_count=9
        )
        service = AIService()
        remaining, limit = service._check_usage_limit(self.free_user)
        self.assertEqual(remaining, 1)

    def test_limit_exceeded(self):
        from apps.ai_assistant.models import AIUsageLog
        from apps.ai_assistant.services import AIService
        from django.conf import settings
        AIUsageLog.objects.create(
            user=self.free_user, date=date.today(),
            requests_count=settings.AI_DAILY_FREE_LIMIT
        )
        service = AIService()
        remaining, _ = service._check_usage_limit(self.free_user)
        self.assertEqual(remaining, 0)

    @patch('apps.ai_assistant.services.OpenAI')
    def test_send_message_mock(self, mock_openai_class):
        """Test sending message with mocked OpenAI."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Test response"))],
            usage=MagicMock(total_tokens=50),
        )
        from apps.ai_assistant.services import AIService
        from apps.ai_assistant.models import AIChat
        service = AIService()
        chat = AIChat.objects.create(
            user=self.free_user, chat_type='general', title='Test'
        )
        result = service.send_message(self.free_user, chat, "Hello")
        self.assertEqual(result['response'], "Test response")
        self.assertIn('remaining_requests', result)
