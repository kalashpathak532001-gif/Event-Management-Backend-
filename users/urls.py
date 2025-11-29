from django.urls import path

from .views import ForgotPasswordView, LoginView, ProfileView, RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='user-forgot-password'),
]
