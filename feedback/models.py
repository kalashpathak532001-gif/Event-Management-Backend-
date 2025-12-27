from django.db import models

class Feedback(models.Model):
    name = models.CharField(max_length=120)
    quote = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    role = models.CharField(max_length=120, default="User", blank=True)
    company = models.CharField(max_length=120, default="Community Member", blank=True)
    image = models.CharField(max_length=10, blank=True)  # store initials or URL
    created_at = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.rating}★)"
