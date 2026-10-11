from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.services import AuthService

User = get_user_model()

class RoleBasedAccessControlTestCase(TestCase):
    """Test suite for Role-Based Access Control (RBAC) decorators and DRF permissions."""

    def setUp(self):
        self.donor = AuthService.register_user(
            username='donor_user',
            email='donor@sanjog.org',
            password='Password123!',
            role=User.RoleChoices.DONOR
        )
        self.receiver = AuthService.register_user(
            username='receiver_user',
            email='receiver@sanjog.org',
            password='Password123!',
            role=User.RoleChoices.RECEIVER
        )
        self.volunteer = AuthService.register_user(
            username='volunteer_user',
            email='volunteer@sanjog.org',
            password='Password123!',
            role=User.RoleChoices.VOLUNTEER
        )
        self.admin = User.objects.create_superuser(
            username='admin_user',
            email='admin@sanjog.org',
            password='Password123!',
            role=User.RoleChoices.ADMIN
        )

        self.client = Client()
        self.api_client = APIClient()

    def test_donor_accesses_donor_dashboard(self):
        """Test DONOR role can access /donor/dashboard/."""
        self.client.force_login(self.donor)
        response = self.client.get('/donor/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_donor_blocked_from_receiver_dashboard(self):
        """Test DONOR role is blocked from /receiver/dashboard/ with 403."""
        self.client.force_login(self.donor)
        response = self.client.get('/receiver/dashboard/')
        self.assertEqual(response.status_code, 403)

    def test_receiver_accesses_receiver_dashboard(self):
        """Test RECEIVER role can access /receiver/dashboard/."""
        self.client.force_login(self.receiver)
        response = self.client.get('/receiver/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_receiver_blocked_from_donor_dashboard(self):
        """Test RECEIVER role is blocked from /donor/dashboard/ with 403."""
        self.client.force_login(self.receiver)
        response = self.client.get('/donor/dashboard/')
        self.assertEqual(response.status_code, 403)

    def test_volunteer_accesses_volunteer_dashboard(self):
        """Test VOLUNTEER role can access /volunteer/dashboard/."""
        self.client.force_login(self.volunteer)
        response = self.client.get('/volunteer/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_volunteer_blocked_from_admin_dashboard(self):
        """Test VOLUNTEER role is blocked from /platform-admin/dashboard/ with 403."""
        self.client.force_login(self.volunteer)
        response = self.client.get('/platform-admin/dashboard/')
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_redirected_to_login(self):
        """Test anonymous user accessing restricted dashboard is redirected to login."""
        response = self.client.get('/donor/dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_admin_accesses_admin_dashboard(self):
        """Test ADMIN role can access /platform-admin/dashboard/."""
        self.client.force_login(self.admin)
        response = self.client.get('/platform-admin/dashboard/')
        self.assertEqual(response.status_code, 200)
