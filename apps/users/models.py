"""User models - to'liq ma'lumotlar bilan."""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, telegram_id, **extra_fields):
        if not telegram_id:
            raise ValueError('Telegram ID majburiy')
        user = self.model(telegram_id=telegram_id, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, telegram_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        user = self.model(telegram_id=telegram_id, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    class Language(models.TextChoices):
        UZBEK   = 'uz', "O'zbek"
        RUSSIAN = 'ru', 'Русский'
        ENGLISH = 'en', 'English'

    class Status(models.TextChoices):
        ACTIVE   = 'active',   'Faol'
        BANNED   = 'banned',   'Bloklangan'
        INACTIVE = 'inactive', 'Nofaol'

    class StudyGoal(models.TextChoices):
        UZBEKISTAN = 'uzbekistan', "O'zbekistonda o'qish"
        ABROAD     = 'abroad',     "Chet elda o'qish"
        BOTH       = 'both',       "Ikkalasi ham"

    # ── Telegram ──────────────────────────────────────
    telegram_id       = models.BigIntegerField(unique=True, db_index=True)
    telegram_username = models.CharField(max_length=100, blank=True, null=True)
    first_name        = models.CharField(max_length=100, blank=True, null=True)
    last_name         = models.CharField(max_length=100, blank=True, null=True)
    phone_number      = models.CharField(max_length=20, blank=True, null=True)

    # ── Joylashuv ─────────────────────────────────────
    region  = models.CharField(max_length=100, blank=True, null=True, verbose_name="Viloyat")
    city    = models.CharField(max_length=100, blank=True, null=True, verbose_name="Shahar/Tuman")
    school  = models.CharField(max_length=200, blank=True, null=True, verbose_name="Maktab")
    grade   = models.CharField(max_length=20, blank=True, null=True, verbose_name="Sinf")

    # ── Shaxsiy ───────────────────────────────────────
    age             = models.PositiveSmallIntegerField(null=True, blank=True)
    study_language  = models.CharField(max_length=50, blank=True, null=True)
    streak_days     = models.IntegerField(default=0)
    last_active_date= models.DateField(blank=True, null=True)
    weekly_xp       = models.IntegerField(default=0)
    referred_by     = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="referrals")
    reminder_time   = models.CharField(max_length=10, blank=True, null=True)  # "09:00:00"
    notes           = models.JSONField(default=dict, blank=True)  # {date: {task, done}}

    # ── O'qish maqsadi ────────────────────────────────
    study_goal      = models.CharField(max_length=20, choices=StudyGoal.choices, blank=True, null=True)
    dream_university = models.CharField(max_length=200, blank=True, null=True)
    interests       = models.JSONField(default=list, blank=True)

    # ── Imtihon ma'lumotlari ──────────────────────────
    exam_subjects   = models.JSONField(default=list, blank=True)   # fanlar

    # O'zbekiston uchun
    dtm_subjects    = models.JSONField(default=list, blank=True)   # DTM fanlari
    dtm_score       = models.PositiveIntegerField(null=True, blank=True, verbose_name="DTM ball")
    nat_cert_score  = models.PositiveIntegerField(null=True, blank=True, verbose_name="Milliy sertifikat ball")

    # Xalqaro
    ielts_score     = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    sat_score       = models.PositiveSmallIntegerField(null=True, blank=True)
    toefl_score     = models.PositiveSmallIntegerField(null=True, blank=True)
    other_cert      = models.CharField(max_length=200, blank=True, null=True)
    other_cert_score = models.CharField(max_length=50, blank=True, null=True)

    target_score    = models.PositiveIntegerField(null=True, blank=True)

    # ── Tizim ─────────────────────────────────────────
    language     = models.CharField(max_length=5, choices=Language.choices, default=Language.UZBEK)
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    is_subscribed_to_channels = models.BooleanField(default=False)
    is_premium   = models.BooleanField(default=False)
    premium_until = models.DateTimeField(null=True, blank=True)
    is_admin     = models.BooleanField(default=False)

    # ── XP / Level ────────────────────────────────────
    xp_points    = models.PositiveIntegerField(default=0)
    level        = models.PositiveSmallIntegerField(default=1)
    study_streak = models.PositiveIntegerField(default=0)
    last_study_date = models.DateField(null=True, blank=True)

    # ── Eslatmalar ────────────────────────────────────
    remind_study = models.BooleanField(default=True)
    remind_time  = models.TimeField(null=True, blank=True)
    remind_exam  = models.BooleanField(default=True)

    # ── Auth ──────────────────────────────────────────
    is_active    = models.BooleanField(default=True)
    is_staff     = models.BooleanField(default=False)
    date_joined  = models.DateTimeField(default=timezone.now)
    last_seen    = models.DateTimeField(null=True, blank=True)

    # Onboarding tugadimi?
    onboarding_done = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD  = 'telegram_id'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'
        indexes = [
            models.Index(fields=['telegram_id']),
            models.Index(fields=['status']),
            models.Index(fields=['is_premium']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.telegram_id})"

    @property
    def full_name(self):
        parts = filter(None, [self.first_name, self.last_name])
        return ' '.join(parts) or f'User {self.telegram_id}'

    @property
    def is_premium_active(self):
        if not self.is_premium:
            return False
        if self.premium_until is None:
            return True
        return self.premium_until > timezone.now()

    def add_xp(self, points: int):
        from django.conf import settings
        self.xp_points += points
        thresholds = getattr(settings, 'LEVEL_THRESHOLDS', {})
        for lvl in sorted(thresholds.keys(), reverse=True):
            if self.xp_points >= thresholds[lvl]:
                self.level = lvl
                break
        self.save(update_fields=['xp_points', 'level'])

    def update_streak(self):
        from datetime import date, timedelta
        today = date.today()
        if self.last_study_date == today:
            return
        if self.last_study_date == today - timedelta(days=1):
            self.study_streak += 1
        else:
            self.study_streak = 1
        self.last_study_date = today
        self.save(update_fields=['study_streak', 'last_study_date'])

    def get_certificates_summary(self):
        """Sertifikatlar qisqacha."""
        certs = []
        if self.dtm_score:
            certs.append(f"DTM: {self.dtm_score}")
        if self.nat_cert_score:
            certs.append(f"Milliy sertifikat: {self.nat_cert_score}")
        if self.ielts_score:
            certs.append(f"IELTS: {self.ielts_score}")
        if self.sat_score:
            certs.append(f"SAT: {self.sat_score}")
        if self.toefl_score:
            certs.append(f"TOEFL: {self.toefl_score}")
        if self.other_cert and self.other_cert_score:
            certs.append(f"{self.other_cert}: {self.other_cert_score}")
        return certs


class UserSession(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='session')
    state      = models.CharField(max_length=100, blank=True, null=True)
    data       = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_sessions'


class BannedUser(models.Model):
    user      = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ban')
    reason    = models.TextField()
    banned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bans_issued')
    banned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'banned_users'

    @property
    def is_active(self):
        if self.expires_at is None:
            return True
        return self.expires_at > timezone.now()


class Broadcast(models.Model):
    class Status(models.TextChoices):
        DRAFT     = 'draft',     'Qoralama'
        SCHEDULED = 'scheduled', 'Rejalashtirilgan'
        RUNNING   = 'running',   'Yuborilmoqda'
        COMPLETED = 'completed', 'Bajarildi'
        FAILED    = 'failed',    'Xato'

    class TargetAudience(models.TextChoices):
        ALL     = 'all',     'Hammaga'
        PREMIUM = 'premium', 'Premium'
        FREE    = 'free',    'Bepul'
        ACTIVE  = 'active',  'Faol (7 kun)'

    title           = models.CharField(max_length=200)
    message         = models.TextField()
    photo_url       = models.URLField(blank=True, null=True)
    target_audience = models.CharField(max_length=20, choices=TargetAudience.choices, default=TargetAudience.ALL)
    status          = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    scheduled_at    = models.DateTimeField(null=True, blank=True)
    created_by      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    sent_count      = models.PositiveIntegerField(default=0)
    failed_count    = models.PositiveIntegerField(default=0)
    completed_at    = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'broadcasts'
        ordering = ['-created_at']