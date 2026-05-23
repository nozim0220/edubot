from django.urls import path
from . import views

urlpatterns = [
    path('', views.UniversityListView.as_view(), name='university-list'),
    path('<int:pk>/', views.UniversityDetailView.as_view(), name='university-detail'),
    path('recommendations/', views.recommendations, name='uni-recommendations'),
    path('compare/', views.compare_universities, name='uni-compare'),
    path('<int:uni_id>/save/', views.save_university, name='save-university'),
    path('saved/', views.SavedUniversitiesView.as_view(), name='saved-universities'),
]
