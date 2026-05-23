"""AI Assistant models for EduBot platform."""
from django.db import models
from apps.users.models import User


class AIChat(models.Model):
    """AI conversation sessions."""

    class ChatType(models.TextChoices):
        HOMEWORK_HELP = 'homework', 'Homework Help'
        EXPLAIN_TOPIC = 'explain', 'Explain Topic'
        MATH_SOLVER = 'math', 'Math Solver'
        GRAMMAR_CHECK = 'grammar', 'Grammar Check'
        ESSAY_WRITING = 'essay', 'Essay Writing'
        CAREER_ADVICE = 'career', 'Career Advice'
        STUDY_PLAN = 'study_plan', 'Study Plan'
        GENERAL = 'general', 'General'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_chats')
    chat_type = models.CharField(max_length=20, choices=ChatType.choices, default=ChatType.GENERAL)
    title = models.CharField(max_length=200, blank=True)
    is_saved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_tokens = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'ai_chats'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'is_saved']),
        ]

    def __str__(self):
        return f"{self.user} - {self.chat_type} ({self.created_at.date()})"


class AIMessage(models.Model):
    """Individual messages in an AI chat."""

    class Role(models.TextChoices):
        USER = 'user', 'User'
        ASSISTANT = 'assistant', 'Assistant'
        SYSTEM = 'system', 'System'

    chat = models.ForeignKey(AIChat, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=Role.choices)
    content = models.TextField()
    tokens_used = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_messages'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class AIUsageLog(models.Model):
    """Track AI API usage per user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_usage_logs')
    date = models.DateField()
    requests_count = models.PositiveIntegerField(default=0)
    tokens_used = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'ai_usage_logs'
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user} - {self.date}: {self.requests_count} requests"
