import logging

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    ForgotPasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        self._send_welcome_email(user)

    def _send_welcome_email(self, user):
        host_user = getattr(settings, 'EMAIL_HOST_USER', '')
        host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', host_user)
        if not (host_user and host_password and from_email):
            return

        first_name = user.first_name or user.email
        subject = 'Welcome to PlanSync'
        message = (
            f"Hi {first_name},\n\n"
            "Thanks for registering with PlanSync. You're all set to log in and explore the dashboard.\n\n"
            "If this wasn't you, please contact support immediately."
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as exc:  # pragma: no cover - best effort notification
            logger.warning("Failed to send welcome email to %s: %s", user.email, exc)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].lower()
        password = serializer.validated_data['password']
        user = authenticate(request, username=email, password=password)

        if not user:
            return Response({'detail': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return Response(
            {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # In a production system, you would trigger an email with a reset link.
        return Response(
            {'detail': 'If an account with that email exists, a reset link will be sent shortly.'},
            status=status.HTTP_200_OK,
        )
