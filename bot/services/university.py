"""Bot-level university service (async wrappers)."""
import logging
from asgiref.sync import sync_to_async

logger = logging.getLogger('bot')


async def search_universities_async(query: str = None, country: str = None,
                                     max_budget: float = None, has_scholarship: bool = None):
    """Async wrapper for university search."""
    from apps.universities.services import UniversitySearchService
    return await sync_to_async(
        lambda: list(UniversitySearchService.search(
            query=query, country=country,
            max_budget=max_budget, has_scholarship=has_scholarship,
        )[:15])
    )()


async def get_university_async(uni_id: int):
    """Async wrapper to get university by ID."""
    from apps.universities.models import University
    return await sync_to_async(University.objects.get)(pk=uni_id, is_active=True)


async def toggle_save_async(user, university):
    """Toggle save university for user."""
    from apps.universities.models import SavedUniversity
    existing = await sync_to_async(
        lambda: SavedUniversity.objects.filter(user=user, university=university).first()
    )()
    if existing:
        await sync_to_async(existing.delete)()
        return False
    await sync_to_async(SavedUniversity.objects.create)(user=user, university=university)
    return True
