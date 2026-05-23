"""
Accounts app models.
Full user system with Telegram integration.
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager for Telegram-based auth."""

    def create_user(self, telegram_id, **extra_fields):
        """Create a regular user."""
        if not telegram_id:
            raise ValueError('Telegram ID is required')
        user = self.model(telegram_id=telegram_id, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, telegram_id, password=None, **extra_fields):
        """Create a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.model(telegram_id=telegram_id, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with Telegram integration.
    Primary authentication via Telegram ID.
    """

    class Language(models.TextChoices):
        UZBEK = 'uz', _('Uzbek')
        ENGLISH = 'en', _('English')
        RUSSIAN = 'ru', _('Russian')

    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        BANNED = 'banned', _('Banned')
        SUSPENDED = 'suspended', _('Suspended')

    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    telegram_id = models.BigIntegerField(unique=True, db_index=True, verbose_name=_('Telegram ID'))
    username = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Telegram Username'))
    first_name = models.CharField(max_length=255, blank=True, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=255, blank=True, verbose_name=_('Last Name'))
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Phone Number'))

    # Status
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    is_staff = models.BooleanField(default=False, verbose_name=_('Is Staff'))
    is_premium = models.BooleanField(default=False, verbose_name=_('Is Premium'))
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_('Status')
    )

    # Language preference
    language = models.CharField(
        max_length=5,
        choices=Language.choices,
        default=Language.UZBEK,
        verbose_name=_('Language')
    )

    # Subscription check
    is_subscribed = models.BooleanField(default=False, verbose_name=_('Is Channel Subscribed'))
    subscription_checked_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    last_active = models.DateTimeField(default=timezone.now, verbose_name=_('Last Active'))

    # Ban info
    ban_reason = models.TextField(blank=True, verbose_name=_('Ban Reason'))
    banned_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Banned At'))
    banned_by = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='banned_users',
        verbose_name=_('Banned By')
    )

    objects = UserManager()

    USERNAME_FIELD = 'telegram_id'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['telegram_id']),
            models.Index(fields=['username']),
            models.Index(fields=['is_premium']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'{self.full_name} (@{self.username}) [{self.telegram_id}]'

    @property
    def full_name(self):
        """Return full name of user."""
        parts = [self.first_name, self.last_name]
        return ' '.join(p for p in parts if p).strip() or f'User {self.telegram_id}'

    @property
    def is_banned(self):
        """Check if user is banned."""
        return self.status == self.Status.BANNED

    def ban(self, reason: str, banned_by=None):
        """Ban user."""
        self.status = self.Status.BANNED
        self.is_active = False
        self.ban_reason = reason
        self.banned_at = timezone.now()
        self.banned_by = banned_by
        self.save(update_fields=['status', 'is_active', 'ban_reason', 'banned_at', 'banned_by'])

    def unban(self):
        """Unban user."""
        self.status = self.Status.ACTIVE
        self.is_active = True
        self.ban_reason = ''
        self.banned_at = None
        self.banned_by = None
        self.save(update_fields=['status', 'is_active', 'ban_reason', 'banned_at', 'banned_by'])

    def update_last_active(self):
        """Update last active timestamp."""
        self.last_active = timezone.now()
        self.save(update_fields=['last_active'])


class UserProfile(models.Model):
    """
    Extended user profile for education platform.
    """

    class StudyLanguage(models.TextChoices):
        UZBEK = 'uz', _('Uzbek')
        RUSSIAN = 'ru', _('Russian')
        ENGLISH = 'en', _('English')

    UZBEKISTAN_REGIONS = [
        ('tashkent_city', _("Tashkent City")),
        ('tashkent', _("Tashkent Region")),
        ('andijan', _("Andijan")),
        ('bukhara', _("Bukhara")),
        ('fergana', _("Fergana")),
        ('jizzakh', _("Jizzakh")),
        ('khorezm', _("Khorezm")),
        ('kashkadarya', _("Kashkadarya")),
        ('namangan', _("Namangan")),
        ('navoiy', _("Navoiy")),
        ('samarkand', _("Samarkand")),
        ('surkhandarya', _("Surkhandarya")),
        ('syrdarya', _("Syrdarya")),
        ('karakalpakstan', _("Karakalpakstan")),
    ]

    GRADE_CHOICES = [
        (7, '7'), (8, '8'), (9, '9'), (10, '10'), (11, '11'),
        (12, _('Graduate')),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('User')
    )

    # Personal info
    age = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_('Age'))
    region = models.CharField(
        max_length=50,
        choices=UZBEKISTAN_REGIONS,
        blank=True,
        verbose_name=_('Region')
    )
    school = models.CharField(max_length=255, blank=True, verbose_name=_('School'))
    grade = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=GRADE_CHOICES,
        verbose_name=_('Grade/Class')
    )
    study_language = models.CharField(
        max_length=5,
        choices=StudyLanguage.choices,
        blank=True,
        verbose_name=_('Study Language')
    )

    # Goals
    interests = models.JSONField(default=list, blank=True, verbose_name=_('Interests'))
    dream_university = models.CharField(max_length=255, blank=True, verbose_name=_('Dream University'))
    exam_subjects = models.JSONField(default=list, blank=True, verbose_name=_('Exam Subjects'))
    target_score = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Target Exam Score'))

    # Avatar
    avatar_url = models.URLField(blank=True, verbose_name=_('Avatar URL'))
    bio = models.TextField(blank=True, max_length=500, verbose_name=_('Bio'))

    # Setup completion
    profile_completed = models.BooleanField(default=False, verbose_name=_('Profile Completed'))

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    def __str__(self):
        return f'Profile of {self.user.full_name}'

    @property
    def completion_percentage(self):
        """Calculate profile completion percentage."""
        fields = [
            self.age, self.region, self.school, self.grade,
            self.study_language, self.dream_university,
            bool(self.exam_subjects), self.target_score
        ]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)


class UserXP(models.Model):
    """
    User experience points and level system.
    """

    LEVEL_THRESHOLDS = [
        (1, 0),
        (2, 100),
        (3, 250),
        (4, 500),
        (5, 900),
        (6, 1400),
        (7, 2000),
        (8, 2750),
        (9, 3750),
        (10, 5000),
        (11, 7000),
        (12, 9500),
        (13, 12500),
        (14, 16000),
        (15, 20000),
        (16, 25000),
        (17, 31000),
        (18, 38000),
        (19, 46000),
        (20, 55000),
    ]

    class XPSource(models.TextChoices):
        QUIZ = 'quiz', _('Quiz')
        TEST = 'test', _('Test')
        DAILY_CHALLENGE = 'daily_challenge', _('Daily Challenge')
        STREAK = 'streak', _('Streak')
        PROFILE = 'profile', _('Profile Completion')
        REFERRAL = 'referral', _('Referral')
        BONUS = 'bonus', _('Bonus')

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='xp',
        verbose_name=_('User')
    )
    total_xp = models.PositiveIntegerField(default=0, verbose_name=_('Total XP'))
    level = models.PositiveSmallIntegerField(default=1, verbose_name=_('Level'))
    streak_days = models.PositiveSmallIntegerField(default=0, verbose_name=_('Streak Days'))
    last_activity_date = models.DateField(null=True, blank=True, verbose_name=_('Last Activity Date'))
    longest_streak = models.PositiveSmallIntegerField(default=0, verbose_name=_('Longest Streak'))

    # Statistics
    quizzes_completed = models.PositiveIntegerField(default=0, verbose_name=_('Quizzes Completed'))
    tests_completed = models.PositiveIntegerField(default=0, verbose_name=_('Tests Completed'))
    correct_answers = models.PositiveIntegerField(default=0, verbose_name=_('Correct Answers'))
    total_answers = models.PositiveIntegerField(default=0, verbose_name=_('Total Answers'))
    ai_queries = models.PositiveIntegerField(default=0, verbose_name=_('AI Queries'))

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User XP')
        verbose_name_plural = _('User XPs')

    def __str__(self):
        return f'{self.user.full_name} - Level {self.level} ({self.total_xp} XP)'

    @property
    def accuracy_rate(self):
        """Calculate answer accuracy rate."""
        if self.total_answers == 0:
            return 0
        return round((self.correct_answers / self.total_answers) * 100, 1)

    def add_xp(self, amount: int, source: str = XPSource.BONUS) -> bool:
        """Add XP and check for level up. Returns True if leveled up."""
        self.total_xp += amount
        old_level = self.level
        self.level = self._calculate_level()
        self.save(update_fields=['total_xp', 'level', 'updated_at'])

        # Log XP transaction
        XPTransaction.objects.create(
            user=self.user,
            amount=amount,
            source=source,
            total_after=self.total_xp,
        )

        return self.level > old_level

    def _calculate_level(self) -> int:
        """Calculate level from total XP."""
        level = 1
        for lvl, threshold in self.LEVEL_THRESHOLDS:
            if self.total_xp >= threshold:
                level = lvl
        return level

    @property
    def xp_to_next_level(self):
        """XP needed for next level."""
        current_threshold = 0
        next_threshold = None
        for lvl, threshold in self.LEVEL_THRESHOLDS:
            if lvl == self.level:
                current_threshold = threshold
            if lvl == self.level + 1:
                next_threshold = threshold
                break
        if next_threshold is None:
            return 0  # Max level
        return next_threshold - self.total_xp

    @property
    def level_progress_percentage(self):
        """Progress percentage towards next level."""
        current_threshold = 0
        next_threshold = None
        for lvl, threshold in self.LEVEL_THRESHOLDS:
            if lvl == self.level:
                current_threshold = threshold
            if lvl == self.level + 1:
                next_threshold = threshold
                break
        if next_threshold is None:
            return 100
        range_xp = next_threshold - current_threshold
        earned_xp = self.total_xp - current_threshold
        return min(100, int((earned_xp / range_xp) * 100))


class XPTransaction(models.Model):
    """Log of all XP transactions."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='xp_transactions',
        verbose_name=_('User')
    )
    amount = models.IntegerField(verbose_name=_('XP Amount'))
    source = models.CharField(
        max_length=30,
        choices=UserXP.XPSource.choices,
        verbose_name=_('Source')
    )
    description = models.CharField(max_length=255, blank=True, verbose_name=_('Description'))
    total_after = models.PositiveIntegerField(verbose_name=_('Total XP After'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('XP Transaction')
        verbose_name_plural = _('XP Transactions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f'{self.user.full_name}: +{self.amount} XP ({self.source})'


class TelegramSession(models.Model):
    """
    Store Telegram auth sessions and tokens.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='telegram_session',
        verbose_name=_('User')
    )
    auth_token = models.CharField(max_length=255, unique=True, verbose_name=_('Auth Token'))
    refresh_token = models.CharField(max_length=255, blank=True, verbose_name=_('Refresh Token'))
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(verbose_name=_('Expires At'))
    last_used = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Telegram Session')
        verbose_name_plural = _('Telegram Sessions')

    def __str__(self):
        return f'Session for {self.user.full_name}'

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at


class ChannelSubscription(models.Model):
    """
    Track which channels each user has subscribed to.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='channel_subscriptions',
        verbose_name=_('User')
    )
    channel_id = models.CharField(max_length=100, verbose_name=_('Channel ID'))
    channel_username = models.CharField(max_length=100, blank=True, verbose_name=_('Channel Username'))
    is_subscribed = models.BooleanField(default=False, verbose_name=_('Is Subscribed'))
    checked_at = models.DateTimeField(auto_now=True, verbose_name=_('Checked At'))
    subscribed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Subscribed At'))

    class Meta:
        verbose_name = _('Channel Subscription')
        verbose_name_plural = _('Channel Subscriptions')
        unique_together = [['user', 'channel_id']]
        indexes = [
            models.Index(fields=['user', 'is_subscribed']),
        ]

    def __str__(self):
        return f'{self.user.full_name} -> {self.channel_username} ({"✓" if self.is_subscribed else "✗"})'
