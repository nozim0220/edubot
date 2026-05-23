"""Education serializers."""
from rest_framework import serializers
from .models import Subject, Topic, Question, Test, TestSession, UserProgress, Certificate


class SubjectSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'code', 'name_uz', 'name_ru', 'name_en', 'emoji', 'description', 'question_count']

    def get_question_count(self, obj):
        return obj.questions.filter(is_active=True).count()


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name_uz', 'name_ru', 'name_en', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id', 'subject', 'topic', 'question_type', 'difficulty',
            'text_uz', 'text_ru', 'text_en', 'option_a', 'option_b',
            'option_c', 'option_d', 'image', 'xp_reward',
        ]


class QuestionResultSerializer(QuestionSerializer):
    """Include correct answer (for results only)."""
    explanation_uz = serializers.CharField()
    explanation_en = serializers.CharField()
    accuracy_rate = serializers.FloatField()

    class Meta(QuestionSerializer.Meta):
        fields = QuestionSerializer.Meta.fields + [
            'correct_answer', 'explanation_uz', 'explanation_en', 'accuracy_rate'
        ]


class TestSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = [
            'id', 'title_uz', 'title_ru', 'title_en', 'subject',
            'test_type', 'time_limit_minutes', 'passing_score',
            'is_premium', 'question_count', 'is_daily', 'daily_date',
        ]

    def get_question_count(self, obj):
        return obj.questions.count()


class TestSessionSerializer(serializers.ModelSerializer):
    test = TestSerializer(read_only=True)
    percentage_score = serializers.IntegerField(read_only=True)
    passed = serializers.BooleanField(read_only=True)

    class Meta:
        model = TestSession
        fields = [
            'id', 'test', 'status', 'current_question_index',
            'score', 'total_questions', 'correct_answers', 'xp_earned',
            'percentage_score', 'passed', 'started_at', 'completed_at', 'time_taken_seconds',
        ]


class SubmitAnswerSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    question_id = serializers.IntegerField()
    answer = serializers.CharField(max_length=500)


class UserProgressSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    accuracy_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = UserProgress
        fields = [
            'id', 'subject', 'tests_completed', 'questions_answered',
            'correct_answers', 'total_xp', 'best_score', 'accuracy_rate', 'last_activity',
        ]


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['id', 'cert_type', 'title', 'description', 'issued_at', 'certificate_id']
