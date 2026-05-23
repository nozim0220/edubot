"""University avtomatik yangilash — Celery tasks."""
import logging
from celery import shared_task

logger = logging.getLogger('bot')


@shared_task(bind=True, max_retries=3)
def auto_sync_universities(self):
    """
    Har hafta avtomatik ishlaydi.
    Celery Beat: dushanba kuni 03:00 da.
    """
    try:
        from apps.universities.scrapers import (
            get_all_verified_data, fetch_uz_from_hemis
        )
        from apps.universities.models import University, Faculty

        data  = get_all_verified_data()
        count = 0
        for uni_name, info in data.items():
            faculties = info.pop('faculties', [])
            info.pop('application_deadline_fall', None)
            try:
                u, created = University.objects.update_or_create(
                    name=uni_name, defaults=info
                )
                for f_name, degree, years, fee, lang in faculties:
                    Faculty.objects.get_or_create(
                        university=u, name=f_name,
                        defaults={'degree':degree,'duration_years':years,
                                  'tuition_fee_usd':fee,'language':lang,'is_active':True}
                    )
                count += 1
            except Exception as e:
                logger.error(f"Sync {uni_name}: {e}")

        logger.info(f"Auto sync: {count} ta universitet yangilandi")
        return {'synced': count}

    except Exception as e:
        logger.error(f"Auto sync xato: {e}")
        raise self.retry(exc=e, countdown=3600)
