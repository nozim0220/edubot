"""University admin."""
from django.contrib import admin
from .models import University, Faculty, SavedUniversity, UniversityReview


class FacultyInline(admin.TabularInline):
    model = Faculty
    extra = 1
    fields = ['name', 'degree', 'duration_years', 'tuition_fee_usd', 'language', 'is_active']


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'city', 'world_ranking', 'tuition_fee_usd',
                    'has_scholarships', 'required_ielts', 'is_active', 'is_featured']
    list_filter = ['country', 'has_scholarships', 'is_active', 'is_featured']
    search_fields = ['name', 'city']
    list_editable = ['is_active', 'is_featured']
    inlines = [FacultyInline]
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'name_uz', 'name_ru', 'short_name', 'country', 'city', 'address')}),
        ('Financials', {'fields': ('tuition_fee_usd', 'tuition_fee_uzs', 'has_scholarships', 'scholarship_info')}),
        ('Requirements', {'fields': ('required_ielts', 'required_sat', 'required_toefl', 'required_gpa', 'dtm_passing_score')}),
        ('Rankings', {'fields': ('world_ranking', 'national_ranking', 'qs_ranking', 'the_ranking')}),
        ('Deadlines', {'fields': ('application_deadline_fall', 'application_deadline_spring')}),
        ('Links', {'fields': ('website', 'application_url')}),
        ('Media', {'fields': ('logo', 'cover_image')}),
        ('Description', {'fields': ('description_uz', 'description_ru', 'description_en')}),
        ('Stats', {'fields': ('total_students', 'international_students', 'founded_year')}),
        ('Status', {'fields': ('is_active', 'is_featured')}),
    )


@admin.register(SavedUniversity)
class SavedUniversityAdmin(admin.ModelAdmin):
    list_display = ['user', 'university', 'saved_at']
    list_filter = ['university__country']
    search_fields = ['user__telegram_id', 'university__name']


@admin.register(UniversityReview)
class UniversityReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'university', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved']
    list_editable = ['is_approved']
