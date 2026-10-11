from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser

class SystemHealthTestCase(TestCase):
    """Base system health check suite for Phase 1 verification."""
    
    def setUp(self):
        self.client = Client()

    def test_health_endpoint_returns_200(self):
        """Verify root health check endpoint returns 200 OK and healthy status."""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['system'], 'SANJOG Food Rescue OS')

    def test_api_v1_health_endpoint_returns_200(self):
        """Verify API v1 namespace health endpoint responds correctly."""
        response = self.client.get('/api/v1/health/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')

    def test_custom_user_model_instantiation(self):
        """Verify CustomUser model foundation creates instances with role attributes."""
        user = CustomUser.objects.create_user(
            username='testdonor',
            email='donor@sanjog.org',
            password='Password123!',
            role=CustomUser.RoleChoices.DONOR
        )
        self.assertEqual(user.username, 'testdonor')
        self.assertTrue(user.is_donor)
        self.assertFalse(user.is_receiver)
        self.assertEqual(str(user), 'testdonor (Food Donor)')
