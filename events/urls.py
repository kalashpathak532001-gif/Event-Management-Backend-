from django.urls import path

from .views import EventDetailView, EventListCreateView, EventReminderView

urlpatterns = [
    path('', EventListCreateView.as_view(), name='event-list-create'),
    path('<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('<int:pk>/remind/', EventReminderView.as_view(), name='event-reminder'),
]
