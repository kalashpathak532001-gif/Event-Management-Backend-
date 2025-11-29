from datetime import timedelta

from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from events.models import Event


class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()
        base_queryset = Event.objects.all() if user.is_admin or user.is_staff else Event.objects.filter(created_by=user)

        total_events = base_queryset.count()
        upcoming_events = base_queryset.filter(event_date__gte=now).count()
        past_week_events = base_queryset.filter(event_date__range=(now - timedelta(days=7), now)).count()

        recent_events = base_queryset.order_by('-event_date')[:5]
        recent_events_payload = [
            {
                'id': event.id,
                'title': event.title,
                'event_date': event.event_date,
                'created_by': event.created_by.get_full_name() or event.created_by.email,
            }
            for event in recent_events
        ]

        monthly_breakdown = []
        for month_delta in range(0, 6):
            month_start = (now - timedelta(days=30 * month_delta)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = (month_start + timedelta(days=32)).replace(day=1)
            count = base_queryset.filter(event_date__gte=month_start, event_date__lt=next_month).count()
            monthly_breakdown.append(
                {
                    'label': month_start.strftime('%b %Y'),
                    'value': count,
                }
            )

        stats = {
            'summary': {
                'total_events': total_events,
                'upcoming_events': upcoming_events,
                'past_week_events': past_week_events,
            },
            'recent_events': recent_events_payload,
            'monthly_breakdown': list(reversed(monthly_breakdown)),
            'utilization': {
                'planned': min(total_events * 5, 100),
                'completed': min(past_week_events * 10, 100),
                'pending': max(100 - min(total_events * 5, 100), 0),
            },
        }

        return Response(stats, status=status.HTTP_200_OK)
