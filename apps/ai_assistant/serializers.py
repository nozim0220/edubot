"""AI Assistant serializers."""
from rest_framework import serializers
from .models import AIChat, AIMessage


class AIMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMessage
        fields = ['id', 'role', 'content', 'tokens_used', 'created_at']


class AIChatSerializer(serializers.ModelSerializer):
    messages = AIMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = AIChat
        fields = ['id', 'chat_type', 'title', 'is_saved', 'total_tokens',
                  'created_at', 'updated_at', 'messages', 'message_count']

    def get_message_count(self, obj):
        return obj.messages.count()


class AIChatListSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = AIChat
        fields = ['id', 'chat_type', 'title', 'is_saved', 'total_tokens',
                  'created_at', 'updated_at', 'message_count']

    def get_message_count(self, obj):
        return obj.messages.count()


class SendMessageSerializer(serializers.Serializer):
    chat_type = serializers.ChoiceField(
        choices=AIChat.ChatType.choices,
        default=AIChat.ChatType.GENERAL,
    )
    chat_id = serializers.IntegerField(required=False, allow_null=True)
    message = serializers.CharField(max_length=5000)
