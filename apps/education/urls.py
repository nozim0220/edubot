from django.urls import path
from . import views

urlpatterns = [
    path('subjects/', views.SubjectListView.as_view(), name='subject-list'),
    path('tests/', views.TestListView.as_view(), name='test-list'),
    path('tests/<int:test_id>/start/', views.start_test, name='start-test'),
    path('sessions/answer/', views.submit_answer, name='submit-answer'),
    path('sessions/<int:session_id>/complete/', views.complete_test, name='complete-test'),
    path('progress/', views.my_progress, name='my-progress'),
    path('daily/', views.daily_challenge, name='daily-challenge'),
    path('certificates/', views.MyCertificatesView.as_view(), name='my-certificates'),
    path('history/', views.MyTestHistoryView.as_view(), name='test-history'),
]
