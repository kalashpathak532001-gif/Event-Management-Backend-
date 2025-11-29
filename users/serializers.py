from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_admin',
            'is_staff',
            'date_joined',
        )
        read_only_fields = ('id', 'username', 'is_staff', 'date_joined')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    is_admin = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'is_admin')

    def create(self, validated_data):
        email = validated_data.get('email').lower()
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        is_admin = validated_data.get('is_admin', False)
        password = validated_data['password']

        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        if is_admin:
            user.is_staff = True
            user.is_admin = True
            user.save(update_fields=['is_staff', 'is_admin'])
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
