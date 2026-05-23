"""Integration tests for API endpoints."""
import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


@pytest.mark.django_db
class TestAuthEndpoints(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_telegram_auth_creates_user(self):
        response = self.client.post('/api/v1/auth/telegram/', {
            'id': 123456789,
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'auth_date': 1700000000,
            'hash': 'fakehash',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(response.data.get('is_new_user'))

    def test_telegram_auth_returns_existing_user(self):
        from apps.users.models import User
        User.objects.create(telegram_id=987654321, first_name='Existing')
        response = self.client.post('/api/v1/auth/telegram/', {
            'id': 987654321,
            'first_name': 'Existing',
            'auth_date': 1700000000,
            'hash': 'fakehash',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data.get('is_new_user'))


@pytest.mark.django_db
class TestUserProfileEndpoints(TestCase):
    def setUp(self):
        from apps.users.models import User
        from rest_framework_simplejwt.tokens import RefreshToken
        self.user = User.objects.create(telegram_id=111111111, first_name="Test")
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

    def test_get_profile(self):
        response = self.client.get('/api/v1/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['telegram_id'], 111111111)

    def test_update_profile(self):
        response = self.client.patch('/api/v1/users/me/', {
            'age': 20,
            'region': 'Tashkent',
            'school': 'School #1',
            'dream_university': 'MIT',
            'target_score': 189,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.age, 20)
        self.assertEqual(self.user.region, 'Tashkent')

    def test_get_leaderboard(self):
        response = self.client.get('/api/v1/users/leaderboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('leaderboard', response.data)
        self.assertIn('my_rank', response.data)


@pytest.mark.django_db
class TestEducationEndpoints(TestCase):
    def setUp(self):
        from apps.users.models import User
        from apps.education.models import Subject, Question, Test, TestQuestion
        from rest_framework_simplejwt.tokens import RefreshToken

        self.user = User.objects.create(telegram_id=222222222, first_name="Student")
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

        self.subject = Subject.objects.create(
            code='math', name_uz='Matematika',
            name_ru='Математика', name_en='Mathematics',
            emoji='🔢', is_active=True, order=1,
        )
        self.question = Question.objects.create(
            subject=self.subject, text_uz='1+1=?',
            option_a='1', option_b='2', option_c='3', option_d='4',
            correct_answer='B', xp_reward=10, is_active=True,
        )
        self.test = Test.objects.create(
            title_uz='Math Quiz', subject=self.subject,
            test_type='quiz', passing_score=50, is_active=True,
        )
        TestQuestion.objects.create(test=self.test, question=self.question, order=1)

    def test_list_subjects(self):
        response = self.client.get('/api/v1/education/subjects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_list_tests(self):
        response = self.client.get('/api/v1/education/tests/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_start_test(self):
        response = self.client.post(f'/api/v1/education/tests/{self.test.pk}/start/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('session', response.data)
        self.assertIn('questions', response.data)

    def test_full_quiz_flow(self):
        # Start
        r1 = self.client.post(f'/api/v1/education/tests/{self.test.pk}/start/')
        self.assertEqual(r1.status_code, 200)
        session_id = r1.data['session']['id']

        # Answer
        r2 = self.client.post('/api/v1/education/sessions/answer/', {
            'session_id': session_id,
            'question_id': self.question.pk,
            'answer': 'B',
        })
        self.assertEqual(r2.status_code, 200)
        self.assertTrue(r2.data['result']['is_correct'])

        # Complete
        r3 = self.client.post(f'/api/v1/education/sessions/{session_id}/complete/')
        self.assertEqual(r3.status_code, 200)
        self.assertEqual(r3.data['result']['correct_answers'], 1)
        self.assertEqual(r3.data['result']['score'], 100)


@pytest.mark.django_db
class TestUniversityEndpoints(TestCase):
    def setUp(self):
        from apps.users.models import User
        from apps.universities.models import University
        from rest_framework_simplejwt.tokens import RefreshToken

        self.user = User.objects.create(telegram_id=333333333, first_name="Seeker")
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

        self.uni = University.objects.create(
            name="Oxford", country="GB", city="Oxford",
            tuition_fee_usd="35000", has_scholarships=True,
            world_ranking=3, is_active=True,
        )

    def test_list_universities(self):
        response = self.client.get('/api/v1/universities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_search_by_name(self):
        response = self.client.get('/api/v1/universities/?q=Oxford')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_university_detail(self):
        response = self.client.get(f'/api/v1/universities/{self.uni.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Oxford")

    def test_save_university(self):
        response = self.client.post(f'/api/v1/universities/{self.uni.pk}/save/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['saved'])

    def test_unsave_university(self):
        self.client.post(f'/api/v1/universities/{self.uni.pk}/save/')
        response = self.client.delete(f'/api/v1/universities/{self.uni.pk}/save/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['saved'])

    def test_saved_universities_list(self):
        self.client.post(f'/api/v1/universities/{self.uni.pk}/save/')
        response = self.client.get('/api/v1/universities/saved/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
