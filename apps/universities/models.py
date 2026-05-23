"""University models for EduBot platform."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class University(models.Model):
    """University database."""

    class CountryChoices(models.TextChoices):
        UZBEKISTAN = 'UZ', 'Uzbekistan'
        USA = 'US', 'United States'
        UK = 'GB', 'United Kingdom'
        GERMANY = 'DE', 'Germany'
        RUSSIA = 'RU', 'Russia'
        SOUTH_KOREA = 'KR', 'South Korea'
        TURKEY = 'TR', 'Turkey'
        CHINA = 'CN', 'China'
        JAPAN = 'JP', 'Japan'
        MALAYSIA = 'MY', 'Malaysia'
        OTHER = 'OT', 'Other'

    name = models.CharField(max_length=300)
    name_uz = models.CharField(max_length=300, blank=True)
    name_ru = models.CharField(max_length=300, blank=True)
    short_name = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=5, choices=CountryChoices.choices)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True)

    # Financials
    tuition_fee_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tuition_fee_uzs = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    has_scholarships = models.BooleanField(default=False)
    scholarship_info = models.TextField(blank=True)
    scholarship_coverage = models.CharField(max_length=200, blank=True)

    # Requirements
    required_ielts = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    required_sat = models.PositiveSmallIntegerField(null=True, blank=True)
    required_toefl = models.PositiveSmallIntegerField(null=True, blank=True)
    required_gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    dtm_passing_score = models.PositiveSmallIntegerField(null=True, blank=True)

    # Ranking
    world_ranking = models.PositiveIntegerField(null=True, blank=True)
    national_ranking = models.PositiveSmallIntegerField(null=True, blank=True)
    qs_ranking = models.PositiveIntegerField(null=True, blank=True)
    the_ranking = models.PositiveIntegerField(null=True, blank=True)

    # Deadlines
    application_deadline_fall = models.DateField(null=True, blank=True)
    application_deadline_spring = models.DateField(null=True, blank=True)

    # Links
    website = models.URLField(blank=True)
    application_url = models.URLField(blank=True)

    # Media
    logo = models.ImageField(upload_to='universities/logos/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='universities/covers/', null=True, blank=True)

    # Description
    description_uz = models.TextField(blank=True)
    description_ru = models.TextField(blank=True)
    description_en = models.TextField(blank=True)

    # Stats
    total_students = models.PositiveIntegerField(null=True, blank=True)
    international_students = models.PositiveIntegerField(null=True, blank=True)
    founded_year = models.PositiveSmallIntegerField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'universities'
        verbose_name = _('University')
        verbose_name_plural = _('Universities')
        ordering = ['world_ranking', 'name']
        indexes = [
            models.Index(fields=['country']),
            models.Index(fields=['world_ranking']),
            models.Index(fields=['is_active', 'is_featured']),
        ]

    def __str__(self):
        return f"{self.name} ({self.country})"

    def get_description(self, lang='en'):
        return getattr(self, f'description_{lang}', self.description_en) or self.description_en

    def get_name(self, lang='en'):
        if lang == 'uz' and self.name_uz:
            return self.name_uz
        if lang == 'ru' and self.name_ru:
            return self.name_ru
        return self.name


class Faculty(models.Model):
    """University faculties and programs."""
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='faculties')
    name = models.CharField(max_length=200)
    name_uz = models.CharField(max_length=200, blank=True)
    name_ru = models.CharField(max_length=200, blank=True)
    degree = models.CharField(max_length=50, default='Bachelor')
    duration_years = models.PositiveSmallIntegerField(default=4)
    tuition_fee_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    available_seats = models.PositiveSmallIntegerField(null=True, blank=True)
    language = models.CharField(max_length=50, default='English')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'faculties'
        ordering = ['university', 'name']

    def __str__(self):
        return f"{self.university.short_name or self.university.name} - {self.name}"


class SavedUniversity(models.Model):
    """Universities saved by users."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_universities')
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saved_universities'
        unique_together = ['user', 'university']
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user} -> {self.university}"


class UniversityReview(models.Model):
    """User reviews for universities."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='university_reviews')
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'university_reviews'
        unique_together = ['user', 'university']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} rated {self.university}: {self.rating}/5"
