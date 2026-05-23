from django.urls import path
from . import webhook

urlpatterns = [
    path('', webhook.telegram_webhook, name='telegram-webhook'),
]
