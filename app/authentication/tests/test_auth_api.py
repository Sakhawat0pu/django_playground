"""
Test for the authentication APIs.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status

LOGIN_URL = reverse('authentication:login')
LOGOUT_URL = reverse('authentication:logout')
CHANGE_PASSWORD_URL = reverse('authentication:changePassword')
def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)

class PublicAuthApiTests(TestCase):
    """Test the public features of the authentication API."""

    def setup(self):
        self.client = APIClient()

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        user_details = {
            "username": "Test Name",
            "email": "test@example.com",
            "password": "test123",
        }

        self.user = create_user(**user_details)

        payLoad = {"email": user_details["email"], "password": user_details["password"]}

        res = self.client.post(LOGIN_URL, payLoad)
        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""
        user_details = {
            "username": "Test Name",
            "email": "test@example.com",
            "password": "test123",
        }

        create_user(**user_details)

        payLoad = {"email": "test@exmaple.com", "password": "badPass"}
        res = self.client.post(LOGIN_URL, payLoad)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""

        payLoad = {"email": "test@example.com", "password": ""}
        res = self.client.post(LOGIN_URL, payLoad)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

class PrivateAuthApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.user = create_user(
            email="test@exmaple.com",
            password="test123",
            username="Test User",
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_token_association(self):
        self.client.post(LOGIN_URL, {"email": "test@exmaple.com", "password": "test123"})
        token_exists = Token.objects.filter(user=self.user).exists()
        self.assertTrue(token_exists)


    def test_user_logout_successful(self):
        """Test user logout successful"""
        self.client.post(LOGIN_URL, {"email": "test@exmaple.com", "password": "test123"})
        res = self.client.post(LOGOUT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_change_password_successful(self):
        """Test change password successful."""
        res = self.client.put(CHANGE_PASSWORD_URL, {"old_password": "test123", "password": "test12345", "password2": "test12345"})
        user = get_user_model().objects.get(email=self.user.email)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(user.check_password('test12345'))

