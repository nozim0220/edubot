"""University views."""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import University, SavedUniversity
from .serializers import (
    UniversitySerializer, UniversityListSerializer,
    SavedUniversitySerializer, UniversityCompareSerializer,
)
from .services import UniversitySearchService


class UniversityListView(generics.ListAPIView):
    """List and search universities."""
    serializer_class = UniversityListSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['universities'],
        summary="Search universities",
        parameters=[
            OpenApiParameter('q', str, description='Search query'),
            OpenApiParameter('country', str, description='Filter by country code'),
            OpenApiParameter('max_budget', float, description='Max tuition fee in USD'),
            OpenApiParameter('has_scholarship', bool, description='Filter by scholarship'),
        ]
    )
    def get(self, request, *args, **kwargs):
        q = request.query_params.get('q')
        country = request.query_params.get('country')
        max_budget = request.query_params.get('max_budget')
        has_scholarship = request.query_params.get('has_scholarship')

        if max_budget:
            try:
                max_budget = float(max_budget)
            except ValueError:
                max_budget = None

        if has_scholarship is not None:
            has_scholarship = has_scholarship.lower() == 'true'

        queryset = UniversitySearchService.search(
            query=q, country=country,
            max_budget=max_budget, has_scholarship=has_scholarship,
        )
        serializer = UniversityListSerializer(queryset, many=True, context={'request': request})
        return Response({'success': True, 'results': serializer.data, 'count': queryset.count()})


class UniversityDetailView(generics.RetrieveAPIView):
    """Get university details."""
    serializer_class = UniversitySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = University.objects.filter(is_active=True).prefetch_related('faculties')

    @extend_schema(tags=['universities'], summary="University details")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_serializer_context(self):
        return {'request': self.request}


@extend_schema(tags=['universities'], summary="Get AI university recommendations")
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def recommendations(request):
    """Get personalized university recommendations."""
    unis = UniversitySearchService.get_recommendations(request.user)
    serializer = UniversityListSerializer(unis, many=True, context={'request': request})
    return Response({'success': True, 'recommendations': serializer.data})


@extend_schema(tags=['universities'], summary="Compare universities")
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def compare_universities(request):
    """Compare universities side by side."""
    serializer = UniversityCompareSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = UniversitySearchService.compare_universities(serializer.validated_data['university_ids'])
    return Response({'success': True, 'comparison': data})


@extend_schema(tags=['universities'], summary="Save or unsave a university")
@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def save_university(request, uni_id):
    """Toggle save/unsave a university."""
    try:
        university = University.objects.get(pk=uni_id, is_active=True)
    except University.DoesNotExist:
        return Response({'error': 'University not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        saved, created = SavedUniversity.objects.get_or_create(
            user=request.user, university=university,
            defaults={'notes': request.data.get('notes', '')}
        )
        return Response({
            'success': True,
            'saved': True,
            'created': created,
        })
    else:
        SavedUniversity.objects.filter(user=request.user, university=university).delete()
        return Response({'success': True, 'saved': False})


class SavedUniversitiesView(generics.ListAPIView):
    """List user's saved universities."""
    serializer_class = SavedUniversitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedUniversity.objects.filter(
            user=self.request.user
        ).select_related('university')

    @extend_schema(tags=['universities'], summary="My saved universities")
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)
