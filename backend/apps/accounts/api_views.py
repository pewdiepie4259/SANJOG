from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import ScopedRateThrottle
from django.core.exceptions import ValidationError as DjangoValidationError

from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer
from .services import AuthService

class APIRegisterView(APIView):
    """API Endpoint: Register a new user (DONOR, RECEIVER, or VOLUNTEER)."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = AuthService.create_api_token(user)
            return Response({
                'message': 'Registration successful.',
                'token': token.key,
                'user': UserProfileSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APILoginView(APIView):
    """API Endpoint: Authenticate user & return API token + role profile."""
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_login'

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username_or_email = serializer.validated_data['username_or_email']
            password = serializer.validated_data['password']
            client_ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
            
            try:
                user = AuthService.authenticate_user(request, username_or_email, password, client_ip=client_ip)
                token = AuthService.create_api_token(user)
                return Response({
                    'message': 'Login successful.',
                    'token': token.key,
                    'user': UserProfileSerializer(user).data
                }, status=status.HTTP_200_OK)
            except DjangoValidationError as e:
                return Response(e.message_dict if hasattr(e, 'message_dict') else {'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APILogoutView(APIView):
    """API Endpoint: Revoke user DRF token and flush active session."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        AuthService.revoke_api_tokens(request.user, request=request)
        return Response({'detail': 'Successfully logged out and token revoked.'}, status=status.HTTP_200_OK)


class APIUserProfileView(APIView):
    """API Endpoint: Fetch current authenticated user profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
