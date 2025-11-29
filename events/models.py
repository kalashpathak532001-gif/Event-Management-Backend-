from django.conf import settings
from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    event_date = models.DateTimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='events',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['event_date']

    def __str__(self) -> str:
        return self.title
