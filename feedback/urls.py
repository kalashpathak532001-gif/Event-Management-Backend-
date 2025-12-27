# feedback/urls.py
from rest_framework import routers
from .views import feedbackViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'', feedbackViewSet, basename='feedback')  
# IMPORTANT: use '' (empty string)

urlpatterns = [
    path('', include(router.urls)),
]
