from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from .services import AuthService

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """DRF serializer for public user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password_confirm', 'role', 'phone_number', 'first_name', 'last_name')
        extra_kwargs = {
            'role': {'required': True},
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        try:
            return AuthService.register_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                role=validated_data['role'],
                phone_number=validated_data.get('phone_number'),
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', '')
            )
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else e.messages)


class UserLoginSerializer(serializers.Serializer):
    """DRF serializer for user login."""
    username_or_email = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    """DRF serializer for user profile details."""
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'role_display', 'phone_number', 'first_name', 'last_name', 'is_email_verified', 'date_joined')
        read_only_fields = ('id', 'username', 'role', 'date_joined')
