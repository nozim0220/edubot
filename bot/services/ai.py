"""Bot-level AI service (async wrappers)."""
import logging
from asgiref.sync import sync_to_async

logger = logging.getLogger('bot')


async def send_ai_message_async(user, chat_id: int, chat_type: str, message: str) -> dict:
    """Async wrapper for AI message sending."""
    from apps.ai_assistant.services import AIService
    from apps.ai_assistant.models import AIChat

    service = AIService()
    chat = await sync_to_async(AIChat.objects.get)(pk=chat_id, user=user)
    return await sync_to_async(service.send_message)(
        user=user, chat=chat, user_message=message
    )


async def get_ai_usage_async(user) -> dict:
    """Async wrapper for AI usage stats."""
    from apps.ai_assistant.services import AIService
    service = AIService()
    return await sync_to_async(service.get_usage_stats)(user)


async def create_ai_chat_async(user, chat_type: str):
    """Async wrapper to create AI chat."""
    from apps.ai_assistant.services import AIService
    service = AIService()
    return await sync_to_async(service.get_or_create_chat)(user=user, chat_type=chat_type)
