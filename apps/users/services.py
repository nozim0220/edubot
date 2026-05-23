"""User business logic services."""
import hashlib
import hmac
import logging
from datetime import timedelta
from typing import Optional

from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache

from .models import User, UserSession, BannedUser

logger = logging.getLogger('apps')


class TelegramAuthService:
    """Handle Telegram authentication."""

    @staticmethod
    def verify_telegram_data(data: dict) -> bool:
        """Verify data received from Telegram Login Widget."""
        check_hash = data.pop('hash', None)
        if not check_hash:
            return False

        data_check_arr = []
        for key, value in sorted(data.items()):
            data_check_arr.append(f"{key}={value}")
        data_check_string = '\n'.join(data_check_arr)

        secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
        expected_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        # Verify timestamp (not older than 1 day)
        auth_date = int(data.get('auth_date', 0))
        if timezone.now().timestamp() - auth_date > 86400:
            return False

        return hmac.compare_digest(check_hash, expected_hash)

    @staticmethod
    @transaction.atomic
    def get_or_create_user(telegram_data: dict) -> tuple[User, bool]:
        """Get or create user from Telegram data."""
        telegram_id = telegram_data['id']

        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                'telegram_username': telegram_data.get('username'),
                'first_name': telegram_data.get('first_name', ''),
                'last_name': telegram_data.get('last_name', ''),
                'is_active': True,
            }
        )

        if not created:
            # Update fields that may have changed
            updated_fields = []
            if telegram_data.get('username') and user.telegram_username != telegram_data['username']:
                user.telegram_username = telegram_data['username']
                updated_fields.append('telegram_username')
            if telegram_data.get('first_name') and user.first_name != telegram_data['first_name']:
                user.first_name = telegram_data['first_name']
                updated_fields.append('first_name')
            if telegram_data.get('last_name') and user.last_name != telegram_data.get('last_name'):
                user.last_name = telegram_data.get('last_name')
                updated_fields.append('last_name')
            if updated_fields:
                user.save(update_fields=updated_fields)

        user.last_seen = timezone.now()
        user.save(update_fields=['last_seen'])

        # Create session if not exists
        UserSession.objects.get_or_create(user=user)

        if created:
            logger.info(f"New user registered: {telegram_id}")
        else:
            logger.debug(f"Existing user logged in: {telegram_id}")

        return user, created


class UserService:
    """User-related business operations."""

    @staticmethod
    def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID, with caching."""
        cache_key = f"user:telegram:{telegram_id}"
        user_id = cache.get(cache_key)
        if user_id:
            try:
                return User.objects.get(pk=user_id)
            except User.DoesNotExist:
                cache.delete(cache_key)

        try:
            user = User.objects.get(telegram_id=telegram_id)
            cache.set(cache_key, user.pk, timeout=300)
            return user
        except User.DoesNotExist:
            return None

    @staticmethod
    def is_user_banned(user: User) -> bool:
        """Check if user is currently banned."""
        try:
            ban = user.ban
            return ban.is_active
        except BannedUser.DoesNotExist:
            return False

    @staticmethod
    def ban_user(user: User, reason: str, banned_by: User, duration_days: int = None) -> BannedUser:
        """Ban a user."""
        expires_at = None
        if duration_days:
            expires_at = timezone.now() + timedelta(days=duration_days)

        ban, _ = BannedUser.objects.update_or_create(
            user=user,
            defaults={
                'reason': reason,
                'banned_by': banned_by,
                'expires_at': expires_at,
                'banned_at': timezone.now(),
            }
        )
        user.status = User.Status.BANNED
        user.save(update_fields=['status'])
        logger.info(f"User {user.telegram_id} banned by {banned_by.telegram_id}: {reason}")
        return ban

    @staticmethod
    def unban_user(user: User) -> None:
        """Unban a user."""
        BannedUser.objects.filter(user=user).delete()
        user.status = User.Status.ACTIVE
        user.save(update_fields=['status'])
        logger.info(f"User {user.telegram_id} unbanned")

    @staticmethod
    def update_profile(user: User, profile_data: dict) -> User:
        """Update user profile fields."""
        allowed_fields = [
            'age', 'region', 'school', 'grade', 'study_language',
            'interests', 'dream_university', 'exam_subjects', 'target_score',
            'language', 'remind_study', 'remind_time', 'remind_exam',
        ]
        updated = []
        for field in allowed_fields:
            if field in profile_data:
                setattr(user, field, profile_data[field])
                updated.append(field)

        if updated:
            user.save(update_fields=updated)
        return user

    @staticmethod
    def get_leaderboard(limit: int = 10) -> list:
        """Get top users by XP."""
        cache_key = f"leaderboard:top:{limit}"
        result = cache.get(cache_key)
        if result:
            return result

        users = User.objects.filter(
            status=User.Status.ACTIVE
        ).order_by('-xp_points')[:limit].values(
            'id', 'first_name', 'last_name', 'telegram_username',
            'xp_points', 'level', 'study_streak'
        )
        result = list(users)
        cache.set(cache_key, result, timeout=300)
        return result

    @staticmethod
    def get_user_rank(user: User) -> int:
        """Get user's rank in leaderboard."""
        rank = User.objects.filter(
            status=User.Status.ACTIVE,
            xp_points__gt=user.xp_points
        ).count() + 1
        return rank
