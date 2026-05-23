"""Education admin."""
from django.contrib import admin
from .models import Subject, Topic, Question, Test, TestQuestion, TestSession, UserProgress, DailyChallenge, Certificate


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_en', 'emoji', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    search_fields = ['code', 'name_en']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['subject', 'name_en', 'order', 'is_active']
    list_filter = ['subject']
    search_fields = ['name_en', 'name_uz']


class TestQuestionInline(admin.TabularInline):
    model = TestQuestion
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'topic', 'difficulty', 'question_type', 'accuracy_rate', 'is_active', 'created_at']
    list_filter = ['subject', 'difficulty', 'question_type', 'is_active']
    search_fields = ['text_uz', 'text_en']
    readonly_fields = ['times_answered', 'times_correct']

    def accuracy_rate(self, obj):
        return f"{obj.accuracy_rate}%"


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['title_uz', 'subject', 'test_type', 'is_premium', 'is_active', 'is_daily']
    list_filter = ['subject', 'test_type', 'is_premium', 'is_active']
    search_fields = ['title_uz', 'title_en']
    inlines = [TestQuestionInline]


@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'test', 'status', 'score', 'correct_answers', 'total_questions', 'xp_earned', 'completed_at']
    list_filter = ['status']
    search_fields = ['user__telegram_id']
    readonly_fields = ['answers']


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'tests_completed', 'accuracy_rate', 'total_xp', 'best_score']
    list_filter = ['subject']


@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display = ['date', 'test', 'bonus_xp']
    date_hierarchy = 'date'


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['user', 'cert_type', 'title', 'issued_at']
    list_filter = ['cert_type']
    readonly_fields = ['certificate_id', 'issued_at']
