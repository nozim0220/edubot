"""University serializers."""
from rest_framework import serializers
from .models import University, Faculty, SavedUniversity


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'name', 'name_uz', 'name_ru', 'degree', 'duration_years',
                  'tuition_fee_usd', 'available_seats', 'language']


class UniversitySerializer(serializers.ModelSerializer):
    faculties = FacultySerializer(many=True, read_only=True)
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = University
        fields = [
            'id', 'name', 'name_uz', 'name_ru', 'short_name', 'country', 'city',
            'tuition_fee_usd', 'tuition_fee_uzs', 'has_scholarships', 'scholarship_info',
            'required_ielts', 'required_sat', 'required_toefl', 'required_gpa',
            'dtm_passing_score', 'world_ranking', 'national_ranking', 'qs_ranking',
            'application_deadline_fall', 'application_deadline_spring',
            'website', 'application_url', 'logo',
            'description_uz', 'description_ru', 'description_en',
            'total_students', 'international_students', 'founded_year',
            'is_featured', 'faculties', 'is_saved',
        ]

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedUniversity.objects.filter(user=request.user, university=obj).exists()
        return False


class UniversityListSerializer(serializers.ModelSerializer):
    """Minimal serializer for list views."""
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = University
        fields = [
            'id', 'name', 'short_name', 'country', 'city', 'logo',
            'world_ranking', 'tuition_fee_usd', 'has_scholarships',
            'required_ielts', 'required_sat', 'is_featured', 'is_saved',
        ]

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedUniversity.objects.filter(user=request.user, university=obj).exists()
        return False


class SavedUniversitySerializer(serializers.ModelSerializer):
    university = UniversityListSerializer(read_only=True)

    class Meta:
        model = SavedUniversity
        fields = ['id', 'university', 'notes', 'saved_at']


class UniversityCompareSerializer(serializers.Serializer):
    university_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=2,
        max_length=4,
    )
