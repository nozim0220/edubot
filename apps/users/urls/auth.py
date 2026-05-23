from django.urls import path
from apps.users import views

urlpatterns = [
    path('telegram/', views.telegram_auth, name='telegram-auth'),
    path('refresh/', views.token_refresh, name='token-refresh'),
]
