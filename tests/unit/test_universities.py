"""Unit tests for university services."""
import pytest
from django.test import TestCase


@pytest.mark.django_db
class TestUniversitySearch(TestCase):
    def setUp(self):
        from apps.universities.models import University
        self.uni1 = University.objects.create(
            name="Test University", country="UZ", city="Tashkent",
            tuition_fee_usd="5000", has_scholarships=True,
            required_ielts="6.0", world_ranking=100, is_active=True,
        )
        self.uni2 = University.objects.create(
            name="MIT", country="US", city="Cambridge",
            tuition_fee_usd="60000", has_scholarships=True,
            required_ielts="7.5", world_ranking=1, is_active=True,
        )
        self.uni3 = University.objects.create(
            name="Local College", country="UZ", city="Samarkand",
            tuition_fee_usd="2000", has_scholarships=False,
            is_active=True,
        )

    def test_search_by_name(self):
        from apps.universities.services import UniversitySearchService
        results = UniversitySearchService.search(query="MIT")
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().name, "MIT")

    def test_filter_by_country(self):
        from apps.universities.services import UniversitySearchService
        results = UniversitySearchService.search(country="UZ")
        self.assertEqual(results.count(), 2)

    def test_filter_by_budget(self):
        from apps.universities.services import UniversitySearchService
        results = UniversitySearchService.search(max_budget=10000)
        names = [r.name for r in results]
        self.assertIn("Test University", names)
        self.assertIn("Local College", names)
        self.assertNotIn("MIT", names)

    def test_filter_by_scholarship(self):
        from apps.universities.services import UniversitySearchService
        results = UniversitySearchService.search(has_scholarship=True)
        names = [r.name for r in results]
        self.assertIn("Test University", names)
        self.assertIn("MIT", names)
        self.assertNotIn("Local College", names)

    def test_compare_universities(self):
        from apps.universities.services import UniversitySearchService
        data = UniversitySearchService.compare_universities([self.uni1.pk, self.uni2.pk])
        self.assertEqual(len(data), 2)
        ids = [d['id'] for d in data]
        self.assertIn(self.uni1.pk, ids)
        self.assertIn(self.uni2.pk, ids)
