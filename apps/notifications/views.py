from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Notification, ExamDeadline
from rest_framework import serializers

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notif_type', 'title', 'message', 'status', 'scheduled_at', 'sent_at', 'created_at']

class ExamDeadlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamDeadline
        fields = ['id', 'title', 'description', 'deadline_date', 'reminder_days_before', 'is_notified', 'created_at']

class MyNotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')[:50]

class ExamDeadlineListCreateView(generics.ListCreateAPIView):
    serializer_class = ExamDeadlineSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return ExamDeadline.objects.filter(user=self.request.user).order_by('deadline_date')
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ExamDeadlineDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExamDeadlineSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return ExamDeadline.objects.filter(user=self.request.user)
