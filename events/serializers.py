from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Event

User = get_user_model()


class EventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)

    class Meta:
        model = Event
        fields = (
            'id',
            'title',
            'description',
            'event_date',
            'created_by',
            'created_by_name',
            'created_by_email',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'created_by_name', 'created_by_email', 'created_at', 'updated_at')
