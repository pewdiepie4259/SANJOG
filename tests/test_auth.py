from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.services import AuthService

User = get_user_model()

class AuthenticationTestCase(TestCase):
    """Test suite for registration, dual login, rate limiting, and logout."""

    def setUp(self):
        cache.clear()
        self.client = Client()
        self.api_client = APIClient()

    def test_valid_donor_registration(self):
        """Test valid donor registration assigns DONOR role."""
        user = AuthService.register_user(
            username='chef_rajesh',
            email='rajesh@palacehotel.org',
            password='Password123!',
            role=User.RoleChoices.DONOR,
            phone_number='+919876543210'
        )
        self.assertEqual(user.username, 'chef_rajesh')
        self.assertEqual(user.email, 'rajesh@palacehotel.org')
        self.assertTrue(user.is_donor)

    def test_valid_receiver_registration(self):
        """Test valid receiver registration assigns RECEIVER role."""
        user = AuthService.register_user(
            username='sister_maria',
            email='maria@hopeshelter.org',
            password='Password123!',
            role=User.RoleChoices.RECEIVER
        )
        self.assertTrue(user.is_receiver)

    def test_valid_volunteer_registration(self):
        """Test valid volunteer registration assigns VOLUNTEER role."""
        user = AuthService.register_user(
            username='aniket_volunteer',
            email='aniket@volunteer.org',
            password='Password123!',
            role=User.RoleChoices.VOLUNTEER
        )
        self.assertTrue(user.is_volunteer)

    def test_admin_public_registration_blocked(self):
        """Test public registration as ADMIN raises validation error."""
        with self.assertRaises(Exception):
            AuthService.register_user(
                username='fake_admin',
                email='fake@admin.org',
                password='Password123!',
                role=User.RoleChoices.ADMIN
            )

    def test_duplicate_email_registration_rejected(self):
        """Test registration with duplicate email address is rejected."""
        AuthService.register_user(
            username='user1',
            email='duplicate@sanjog.org',
            password='Password123!',
            role=User.RoleChoices.DONOR
        )
        with self.assertRaises(Exception):
            AuthService.register_user(
                username='user2',
                email='DUPLICATE@sanjog.org',  # Case insensitive duplicate check
                password='Password123!',
                role=User.RoleChoices.RECEIVER
            )

    def test_login_with_username_and_email(self):
        """Test dual login using either username or email address."""
        user = AuthService.register_user(
            username='dualloginuser',
            email='dual@sanjog.org',
            password='Password123!',
            role=User.RoleChoices.DONOR
        )
        
        # Test username authentication
        auth_by_username = AuthService.authenticate_user(None, 'dualloginuser', 'Password123!')
        self.assertEqual(auth_by_username, user)

        # Test email authentication
        auth_by_email = AuthService.authenticate_user(None, 'dual@sanjog.org', 'Password123!')
        self.assertEqual(auth_by_email, user)

    def test_login_rate_limiting(self):
        """Test rate limiting enforces lockout after 5 failed attempts."""
        client_ip = '192.168.1.100'
        username = 'target_user'

        # Record 5 failed attempts
        for _ in range(5):
            AuthService.record_failed_login(client_ip, username)

        is_locked, cooldown = AuthService.check_rate_limit(client_ip, username)
        self.assertTrue(is_locked)
        self.assertGreater(cooldown, 0)

    def test_api_login_and_logout(self):
        """Test DRF token login and token revocation logout."""
        user = AuthService.register_user(
            username='apiuser',
            email='api@sanjog.org',
            password='Password123!',
            role=User.RoleChoices.VOLUNTEER
        )

        # Login via API
        response = self.api_client.post('/api/v1/auth/login/', {
            'username_or_email': 'api@sanjog.org',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token_key = response.data['token']

        # Logout via API
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Token {token_key}')
        logout_response = self.api_client.post('/api/v1/auth/logout/')
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        # Verify token was revoked
        me_response = self.api_client.get('/api/v1/auth/me/')
        self.assertEqual(me_response.status_code, status.HTTP_401_UNAUTHORIZED)
