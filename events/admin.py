from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'created_by', 'created_at')
    search_fields = ('title', 'description', 'created_by__email')
    list_filter = ('event_date', 'created_at')
