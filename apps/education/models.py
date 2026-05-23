"""Education models for EduBot platform."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class Subject(models.Model):
    """Academic subject."""

    class SubjectCode(models.TextChoices):
        MATH = 'math', 'Mathematics'
        ENGLISH = 'english', 'English'
        PHYSICS = 'physics', 'Physics'
        CHEMISTRY = 'chemistry', 'Chemistry'
        BIOLOGY = 'biology', 'Biology'
        HISTORY = 'history', 'History'
        IT = 'it', 'Information Technology'
        IELTS = 'ielts', 'IELTS'
        SAT = 'sat', 'SAT'

    code = models.CharField(max_length=20, choices=SubjectCode.choices, unique=True)
    name_uz = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    emoji = models.CharField(max_length=10, default='📚')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'subjects'
        ordering = ['order']

    def __str__(self):
        return self.name_en

    def get_name(self, lang='en'):
        return getattr(self, f'name_{lang}', self.name_en)


class Topic(models.Model):
    """Topic within a subject."""
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    name_uz = models.CharField(max_length=200)
    name_ru = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'topics'
        ordering = ['subject', 'order']

    def __str__(self):
        return f"{self.subject} - {self.name_en}"


class Question(models.Model):
    """Test question with multiple choice."""

    class Difficulty(models.TextChoices):
        EASY = 'easy', 'Easy'
        MEDIUM = 'medium', 'Medium'
        HARD = 'hard', 'Hard'
        EXPERT = 'expert', 'Expert'

    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = 'multiple_choice', 'Multiple Choice'
        TRUE_FALSE = 'true_false', 'True/False'
        SHORT_ANSWER = 'short_answer', 'Short Answer'
        ESSAY = 'essay', 'Essay'

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QuestionType.choices, default=QuestionType.MULTIPLE_CHOICE)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.MEDIUM)

    # Question text in all languages
    text_uz = models.TextField()
    text_ru = models.TextField(blank=True)
    text_en = models.TextField(blank=True)

    # For multiple choice
    option_a = models.TextField(blank=True)
    option_b = models.TextField(blank=True)
    option_c = models.TextField(blank=True)
    option_d = models.TextField(blank=True)
    correct_answer = models.CharField(max_length=1, blank=True)  # A, B, C, D or True/False

    # For short answer / essay
    answer_text = models.TextField(blank=True)
    explanation_uz = models.TextField(blank=True)
    explanation_ru = models.TextField(blank=True)
    explanation_en = models.TextField(blank=True)

    image = models.ImageField(upload_to='questions/', null=True, blank=True)
    xp_reward = models.PositiveSmallIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    times_answered = models.PositiveIntegerField(default=0)
    times_correct = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'questions'
        indexes = [
            models.Index(fields=['subject', 'difficulty']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.subject} - {self.text_uz[:50]}"

    def get_text(self, lang='uz'):
        return getattr(self, f'text_{lang}', self.text_uz) or self.text_uz

    @property
    def accuracy_rate(self):
        if self.times_answered == 0:
            return 0
        return round(self.times_correct / self.times_answered * 100, 1)


class Test(models.Model):
    """A structured test or quiz."""

    class TestType(models.TextChoices):
        QUIZ = 'quiz', 'Quick Quiz'
        MOCK_EXAM = 'mock_exam', 'Mock Exam'
        DAILY_CHALLENGE = 'daily', 'Daily Challenge'
        TIMED = 'timed', 'Timed Test'
        RANDOM = 'random', 'Random Questions'

    title_uz = models.CharField(max_length=200)
    title_ru = models.CharField(max_length=200, blank=True)
    title_en = models.CharField(max_length=200, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='tests')
    test_type = models.CharField(max_length=20, choices=TestType.choices, default=TestType.QUIZ)
    questions = models.ManyToManyField(Question, through='TestQuestion')
    time_limit_minutes = models.PositiveSmallIntegerField(null=True, blank=True)
    passing_score = models.PositiveSmallIntegerField(default=60)
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_daily = models.BooleanField(default=False)
    daily_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'tests'
        indexes = [
            models.Index(fields=['subject', 'is_active']),
            models.Index(fields=['test_type']),
        ]

    def __str__(self):
        return self.title_uz

    def get_title(self, lang='uz'):
        return getattr(self, f'title_{lang}', self.title_uz) or self.title_uz


class TestQuestion(models.Model):
    """Ordered questions within a test."""
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=0)
    points = models.PositiveSmallIntegerField(default=1)

    class Meta:
        db_table = 'test_questions'
        ordering = ['order']
        unique_together = ['test', 'question']


class TestSession(models.Model):
    """Active test session for a user."""

    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        ABANDONED = 'abandoned', 'Abandoned'
        TIMED_OUT = 'timed_out', 'Timed Out'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_sessions')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='sessions')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    current_question_index = models.PositiveSmallIntegerField(default=0)
    answers = models.JSONField(default=dict)  # {question_id: answer}
    score = models.PositiveSmallIntegerField(default=0)
    total_questions = models.PositiveSmallIntegerField(default=0)
    correct_answers = models.PositiveSmallIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_taken_seconds = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'test_sessions'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['test', 'status']),
        ]

    def __str__(self):
        return f"{self.user} - {self.test} ({self.status})"

    @property
    def percentage_score(self):
        if self.total_questions == 0:
            return 0
        return round(self.correct_answers / self.total_questions * 100)

    @property
    def passed(self):
        return self.percentage_score >= self.test.passing_score


class UserProgress(models.Model):
    """Track user's overall progress per subject."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    tests_completed = models.PositiveIntegerField(default=0)
    questions_answered = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    total_xp = models.PositiveIntegerField(default=0)
    best_score = models.PositiveSmallIntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_progress'
        unique_together = ['user', 'subject']

    def __str__(self):
        return f"{self.user} - {self.subject}"

    @property
    def accuracy_rate(self):
        if self.questions_answered == 0:
            return 0
        return round(self.correct_answers / self.questions_answered * 100, 1)


class DailyChallenge(models.Model):
    """Daily challenge for users."""
    date = models.DateField(unique=True)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    bonus_xp = models.PositiveSmallIntegerField(default=100)

    class Meta:
        db_table = 'daily_challenges'
        ordering = ['-date']

    def __str__(self):
        return f"Daily Challenge: {self.date}"


class Certificate(models.Model):
    """Achievement certificates."""

    class CertType(models.TextChoices):
        TEST_MASTER = 'test_master', 'Test Master'
        SUBJECT_EXPERT = 'subject_expert', 'Subject Expert'
        STREAK_WARRIOR = 'streak_warrior', 'Streak Warrior'
        TOP_SCORER = 'top_scorer', 'Top Scorer'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    cert_type = models.CharField(max_length=30, choices=CertType.choices)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_id = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'certificates'
        ordering = ['-issued_at']

    def __str__(self):
        return f"{self.user} - {self.title}"
