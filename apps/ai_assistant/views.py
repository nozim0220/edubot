"""AI Assistant views."""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import AIChat
from .serializers import AIChatSerializer, AIChatListSerializer, SendMessageSerializer
from .services import AIService
from apps.users.exceptions import AILimitExceeded


class AIChatListView(generics.ListAPIView):
    """List user's AI chat history."""
    serializer_class = AIChatListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AIChat.objects.filter(user=self.request.user)

    @extend_schema(tags=['ai'], summary="List AI chats")
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)


class AIChatDetailView(generics.RetrieveDestroyAPIView):
    """Get or delete an AI chat."""
    serializer_class = AIChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AIChat.objects.filter(user=self.request.user)

    @extend_schema(tags=['ai'], summary="Get AI chat details")
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)


@extend_schema(tags=['ai'], summary="Send message to AI assistant")
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_message(request):
    """Send a message to the AI assistant."""
    serializer = SendMessageSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    service = AIService()
    try:
        chat = service.get_or_create_chat(
            user=request.user,
            chat_type=serializer.validated_data['chat_type'],
            chat_id=serializer.validated_data.get('chat_id'),
        )
        result = service.send_message(
            user=request.user,
            chat=chat,
            user_message=serializer.validated_data['message'],
        )
        return Response({
            'success': True,
            'chat_id': chat.pk,
            'response': result['response'],
            'remaining_requests': result['remaining_requests'],
        })
    except AILimitExceeded as e:
        return Response(
            {'error': str(e), 'upgrade_required': not request.user.is_premium_active},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@extend_schema(tags=['ai'], summary="Get AI usage statistics")
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def usage_stats(request):
    """Get current user's AI usage statistics."""
    service = AIService()
    stats = service.get_usage_stats(request.user)
    return Response({'success': True, 'stats': stats})


@extend_schema(tags=['ai'], summary="Toggle save AI chat")
@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def toggle_save_chat(request, chat_id):
    """Toggle save/unsave an AI chat."""
    try:
        chat = AIChat.objects.get(pk=chat_id, user=request.user)
        chat.is_saved = not chat.is_saved
        chat.save(update_fields=['is_saved'])
        return Response({'success': True, 'is_saved': chat.is_saved})
    except AIChat.DoesNotExist:
        return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
