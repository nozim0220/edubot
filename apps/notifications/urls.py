from django.urls import path
from . import views
urlpatterns = [
    path('', views.MyNotificationsView.as_view(), name='my-notifications'),
    path('deadlines/', views.ExamDeadlineListCreateView.as_view(), name='exam-deadlines'),
    path('deadlines/<int:pk>/', views.ExamDeadlineDetailView.as_view(), name='exam-deadline-detail'),
]
