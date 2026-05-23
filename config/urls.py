"""Main URL configuration for EduBot platform."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/', include([
        path('auth/', include('apps.users.urls.auth')),
        path('users/', include('apps.users.urls.users')),
        path('education/', include('apps.education.urls')),
        path('universities/', include('apps.universities.urls')),
        path('payments/', include('apps.payments.urls')),
        path('ai/', include('apps.ai_assistant.urls')),
        path('notifications/', include('apps.notifications.urls')),
    ])),

    # Webhook
    path('webhook/telegram/', include('bot.webhook_urls')),

    # API Schema & Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin customization
admin.site.site_header = "EduBot Admin"
admin.site.site_title = "EduBot Administration"
admin.site.index_title = "Welcome to EduBot Admin"

# Admin analytics API
from apps.users import views_admin
urlpatterns += [
    path('api/v1/admin-api/analytics/', views_admin.analytics_dashboard, name='admin-analytics'),
    path('api/v1/admin-api/broadcast/', views_admin.send_broadcast, name='admin-broadcast'),
    path('api/v1/admin-api/user-growth/', views_admin.user_growth, name='admin-user-growth'),
    path('api/v1/admin-api/subject-stats/', views_admin.subject_stats, name='admin-subject-stats'),
]

# Admin analytics API
from apps.users import views_admin
urlpatterns += [
    path('api/v1/admin-api/analytics/', views_admin.analytics_dashboard, name='admin-analytics'),
    path('api/v1/admin-api/broadcast/', views_admin.send_broadcast, name='admin-broadcast'),
    path('api/v1/admin-api/user-growth/', views_admin.user_growth, name='admin-user-growth'),
    path('api/v1/admin-api/subject-stats/', views_admin.subject_stats, name='admin-subject-stats'),
]
