"""User serializers."""
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Broadcast


class TelegramAuthSerializer(serializers.Serializer):
    """Validate Telegram auth data."""
    id = serializers.IntegerField()
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)
    photo_url = serializers.URLField(required=False, allow_blank=True)
    auth_date = serializers.IntegerField()
    hash = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    """Full user profile serializer."""
    full_name = serializers.ReadOnlyField()
    is_premium_active = serializers.ReadOnlyField()
    rank = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'telegram_id', 'telegram_username', 'first_name', 'last_name',
            'full_name', 'phone_number', 'age', 'region', 'school', 'grade',
            'study_language', 'interests', 'dream_university', 'exam_subjects',
            'target_score', 'language', 'status', 'is_premium', 'is_premium_active',
            'premium_until', 'xp_points', 'level', 'study_streak', 'last_study_date',
            'is_subscribed_to_channels', 'remind_study', 'remind_time', 'remind_exam',
            'date_joined', 'last_seen', 'rank',
        ]
        read_only_fields = [
            'id', 'telegram_id', 'status', 'is_premium', 'premium_until',
            'xp_points', 'level', 'study_streak', 'date_joined', 'last_seen',
            'is_subscribed_to_channels',
        ]

    def get_rank(self, obj):
        from .services import UserService
        return UserService.get_user_rank(obj)


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    class Meta:
        model = User
        fields = [
            'age', 'region', 'school', 'grade', 'study_language',
            'interests', 'dream_university', 'exam_subjects', 'target_score',
            'language', 'remind_study', 'remind_time', 'remind_exam',
        ]


class TokenResponseSerializer(serializers.Serializer):
    """JWT token response."""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserProfileSerializer()


class LeaderboardEntrySerializer(serializers.Serializer):
    """Leaderboard entry."""
    id = serializers.IntegerField()
    first_name = serializers.CharField(allow_null=True)
    last_name = serializers.CharField(allow_null=True)
    telegram_username = serializers.CharField(allow_null=True)
    xp_points = serializers.IntegerField()
    level = serializers.IntegerField()
    study_streak = serializers.IntegerField()


class BroadcastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Broadcast
        fields = '__all__'
        read_only_fields = ['created_by', 'sent_count', 'failed_count', 'completed_at']
