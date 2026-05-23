"""University search and recommendation services."""
import logging
from typing import List, Optional
from django.db.models import Q, QuerySet
from django.core.cache import cache

from .models import University, SavedUniversity
from apps.users.models import User

logger = logging.getLogger('apps')


class UniversitySearchService:
    """Handle university search and filtering."""

    @staticmethod
    def search(query: str = None, country: str = None, max_budget: float = None,
               min_ielts: float = None, max_ielts: float = None,
               has_scholarship: bool = None) -> QuerySet:
        """Search universities with filters."""
        qs = University.objects.filter(is_active=True)

        if query:
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(name_uz__icontains=query) |
                Q(city__icontains=query) |
                Q(description_en__icontains=query)
            )

        if country:
            qs = qs.filter(country=country)

        if max_budget is not None:
            qs = qs.filter(
                Q(tuition_fee_usd__lte=max_budget) | Q(tuition_fee_usd__isnull=True)
            )

        if min_ielts is not None:
            qs = qs.filter(
                Q(required_ielts__lte=min_ielts) | Q(required_ielts__isnull=True)
            )

        if max_ielts is not None:
            qs = qs.filter(required_ielts__lte=max_ielts)

        if has_scholarship is not None:
            qs = qs.filter(has_scholarships=has_scholarship)

        return qs.select_related().prefetch_related('faculties').order_by('world_ranking', 'name')

    @staticmethod
    def get_recommendations(user: User, limit: int = 5) -> List[University]:
        """AI-based university recommendations for a user."""
        cache_key = f"uni_recommendations:{user.pk}"
        cached = cache.get(cache_key)
        if cached:
            return University.objects.filter(pk__in=cached)

        qs = University.objects.filter(is_active=True)

        # Filter by IELTS if user has target
        if user.target_score:
            ielts_score = user.target_score / 9.0 * 9.0  # normalize
            qs = qs.filter(
                Q(required_ielts__lte=ielts_score + 0.5) | Q(required_ielts__isnull=True)
            )

        # Prioritize featured and ranked universities
        qs = qs.order_by('world_ranking')[:limit * 3]

        import random
        uni_list = list(qs)
        if len(uni_list) > limit:
            uni_list = random.sample(uni_list, limit)

        cache.set(cache_key, [u.pk for u in uni_list], timeout=3600)
        return uni_list

    @staticmethod
    def compare_universities(ids: List[int]) -> List[dict]:
        """Compare multiple universities side by side."""
        universities = University.objects.filter(pk__in=ids, is_active=True)
        return list(universities.values(
            'id', 'name', 'country', 'city', 'world_ranking',
            'tuition_fee_usd', 'required_ielts', 'required_sat',
            'has_scholarships', 'website', 'application_deadline_fall',
        ))
