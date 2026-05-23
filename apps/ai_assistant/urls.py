from django.urls import path
from . import views

urlpatterns = [
    path('chats/', views.AIChatListView.as_view(), name='ai-chat-list'),
    path('chats/<int:pk>/', views.AIChatDetailView.as_view(), name='ai-chat-detail'),
    path('chat/<int:chat_id>/save/', views.toggle_save_chat, name='ai-chat-save'),
    path('send/', views.send_message, name='ai-send'),
    path('usage/', views.usage_stats, name='ai-usage'),
]
