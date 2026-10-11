from django.contrib.auth import get_user_model, authenticate, login as django_login, logout as django_logout
from django.core.exceptions import ValidationError
from django.core.cache import cache
from rest_framework.authtoken.models import Token

User = get_user_model()

class AuthService:
    """
    Business Logic Service Layer for SANJOG Authentication and User Operations.
    Decouples business logic from views and serializers.
    """
    
    RATE_LIMIT_MAX_ATTEMPTS = 5
    RATE_LIMIT_COOLDOWN_SECONDS = 900  # 15 minutes lockout
    RATE_LIMIT_WINDOW_SECONDS = 300     # 5 minutes window

    @classmethod
    def register_user(cls, username, email, password, role, phone_number=None, first_name='', last_name=''):
        """
        Registers a new user on the platform.
        Enforces role restrictions and email uniqueness at service layer.
        """
        # Block public self-registration as ADMIN
        if role == User.RoleChoices.ADMIN or role == 'ADMIN':
            raise ValidationError({'role': 'Public registration as Platform Administrator is forbidden.'})
        
        # Enforce valid role choice
        valid_roles = [User.RoleChoices.DONOR, User.RoleChoices.RECEIVER, User.RoleChoices.VOLUNTEER]
        if role not in valid_roles:
            raise ValidationError({'role': f'Invalid registration role. Must be one of {valid_roles}'})

        # Normalize and validate email uniqueness
        normalized_email = email.strip().lower()
        if User.objects.filter(email__iexact=normalized_email).exists():
            raise ValidationError({'email': 'A user account with this email address already exists.'})

        # Normalize and validate username uniqueness
        normalized_username = username.strip()
        if User.objects.filter(username__iexact=normalized_username).exists():
            raise ValidationError({'username': 'A user with this username already exists.'})

        # Validate phone number uniqueness if provided
        if phone_number and phone_number.strip():
            cleaned_phone = phone_number.strip()
            if User.objects.filter(phone_number=cleaned_phone).exists():
                raise ValidationError({'phone_number': 'A user account with this phone number already exists.'})

        # Create user instance
        user = User.objects.create_user(
            username=normalized_username,
            email=normalized_email,
            password=password,
            role=role,
            phone_number=phone_number.strip() if phone_number else None,
            first_name=first_name.strip(),
            last_name=last_name.strip()
        )
        return user

    @classmethod
    def check_rate_limit(cls, client_ip, username_or_email):
        """
        Checks if login attempts for IP/username combination exceed allowed threshold.
        Returns (is_locked, remaining_seconds).
        """
        cache_key = f"login_attempts_{client_ip}_{username_or_email.strip().lower()}"
        lockout_key = f"login_lockout_{client_ip}_{username_or_email.strip().lower()}"

        if cache.get(lockout_key):
            return True, cls.RATE_LIMIT_COOLDOWN_SECONDS

        attempts = cache.get(cache_key, 0)
        if attempts >= cls.RATE_LIMIT_MAX_ATTEMPTS:
            # Set lockout marker
            cache.set(lockout_key, True, cls.RATE_LIMIT_COOLDOWN_SECONDS)
            return True, cls.RATE_LIMIT_COOLDOWN_SECONDS

        return False, 0

    @classmethod
    def record_failed_login(cls, client_ip, username_or_email):
        """Increments failed login counter in cache."""
        cache_key = f"login_attempts_{client_ip}_{username_or_email.strip().lower()}"
        attempts = cache.get(cache_key, 0) + 1
        cache.set(cache_key, attempts, cls.RATE_LIMIT_WINDOW_SECONDS)

    @classmethod
    def clear_failed_logins(cls, client_ip, username_or_email):
        """Clears failed login counters upon successful authentication."""
        cache_key = f"login_attempts_{client_ip}_{username_or_email.strip().lower()}"
        lockout_key = f"login_lockout_{client_ip}_{username_or_email.strip().lower()}"
        cache.delete(cache_key)
        cache.delete(lockout_key)

    @classmethod
    def authenticate_user(cls, request, username_or_email, password, client_ip='127.0.0.1'):
        """
        Authenticates user with rate-limiting protection.
        """
        is_locked, cooldown = cls.check_rate_limit(client_ip, username_or_email)
        if is_locked:
            raise ValidationError({'non_field_errors': f'Too many failed login attempts. Account temporarily locked for 15 minutes.'})

        user = authenticate(request, username=username_or_email, password=password)
        if not user:
            cls.record_failed_login(client_ip, username_or_email)
            raise ValidationError({'non_field_errors': 'Invalid credentials provided.'})

        if not user.is_active:
            raise ValidationError({'non_field_errors': 'This user account is inactive. Please contact platform admin.'})

        cls.clear_failed_logins(client_ip, username_or_email)
        return user

    @classmethod
    def create_api_token(cls, user):
        """Retrieves or creates DRF Auth Token for API clients."""
        token, _ = Token.objects.get_or_create(user=user)
        return token

    @classmethod
    def revoke_api_tokens(cls, user, request=None):
        """
        Revokes user DRF tokens and flushes session data.
        """
        if user and user.is_authenticated:
            Token.objects.filter(user=user).delete()
        if request and hasattr(request, 'session'):
            django_logout(request)
