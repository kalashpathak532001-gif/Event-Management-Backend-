from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event
from .notifications import send_event_created_notification, send_event_manual_reminder
from .serializers import EventSerializer


class EventListCreateView(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if self.request.method in permissions.SAFE_METHODS:
            return Event.objects.all()
        if getattr(user, 'is_admin', False) or user.is_staff or user.is_superuser:
            return Event.objects.all()
        return Event.objects.filter(created_by=user)

    def perform_create(self, serializer):
        event = serializer.save(created_by=self.request.user)
        send_event_created_notification(event)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if self.request.method in permissions.SAFE_METHODS:
            return Event.objects.all()
        if getattr(user, 'is_admin', False) or user.is_staff or user.is_superuser:
            return Event.objects.all()
        return Event.objects.filter(created_by=user)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)


class EventReminderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if not self._user_can_manage(event, request.user):
            return Response({'detail': 'Not authorized to send reminders for this event.'}, status=status.HTTP_403_FORBIDDEN)

        sent = send_event_manual_reminder(event, triggered_by=request.user)
        return Response(
            {'detail': f'Reminder sent to {sent} recipients.'},
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _user_can_manage(event, user):
        if getattr(user, 'is_admin', False) or user.is_staff or user.is_superuser:
            return True
        return event.created_by_id == user.id
