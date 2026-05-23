from django.urls import path
from . import views

urlpatterns = [
    path('plans/', views.PremiumPlanListView.as_view(), name='premium-plans'),
    path('create/', views.create_payment, name='create-payment'),
    path('history/', views.my_payments, name='my-payments'),
    path('subscription/', views.my_subscription, name='my-subscription'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe-webhook'),
    path('webhook/click/', views.click_webhook, name='click-webhook'),
]
