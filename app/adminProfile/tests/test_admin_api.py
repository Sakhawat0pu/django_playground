"""
Test for the admin profile APIs.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import AdminProfile, Location

CREATE_ADMIN_PROFILE_URL = reverse("adminProfile:create")
ME_URL = reverse("adminProfile:me")

payload = {
	"location": {
        "street": "test street",
		"city": "test",
		"state": "test",
		"country": "test"
	},
	"user": {
		"username": "test_username",
		"email": "test_user@example.com",
		"password": "test12345"
	},
	"firstName": "test",
	"middleName": "test",
	"lastName": "test",
	"email": "test_user@example.com",
	"gender": "male",
	"dob": "2024-03-22",
	"contactNo": "0039928",
	"profileImg": "example.jpg",
	"interests": [
		"fishing"
	]
}

update_payload = {
	"user": {
		"password": "test123"
	},
	"firstName": "Updated Fname",
	"middleName": "Updated Mname",
	"lastName": "Updated Lname",
}

def create_admin():
    """Create and return a new admin"""
    payload_copy = payload.copy()
    user_data = payload_copy.pop('user')
    location_data = payload_copy.pop('location')

    user = get_user_model().objects.create_user(**user_data, role="Admin", is_staff=True)
    location = Location.objects.create(**location_data)
    adminProfile = AdminProfile.objects.create(user=user, location=location, **payload_copy)
    return adminProfile


class PublicUserApiTests(TestCase):
    """Test the public features of the admin profile API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_admin_profile_successful(self):
        """Test creating a admin is successful"""

        res = self.client.post(CREATE_ADMIN_PROFILE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload["email"])
        adminProfile = AdminProfile.objects.get(email=payload["email"])

        self.assertTrue(user.is_staff);
        self.assertEqual(user.role, "Admin")
        self.assertTrue(user.check_password(payload["user"]["password"]))
        self.assertEqual(adminProfile.firstName, payload["firstName"])
        self.assertNotIn("password", res.data)

    def test_user_with_email_exists_error(self):
        """Test error returns if user with email exists"""
        create_admin();

        res = self.client.post(CREATE_ADMIN_PROFILE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password is less than 5 chars."""
        payload_copy = payload.copy()
        payload_copy["user"]["password"] = '123'
        res = self.client.post(CREATE_ADMIN_PROFILE_URL, payload_copy, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        admin_exists = get_user_model().objects.filter(email=payload["email"]).exists()

        self.assertFalse(admin_exists)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for admins."""

        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.user = create_admin()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data['email'],
            self.user.email
        )

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_admin_profile(self):
        """Test updating the admin profile for authenticated user."""

        res = self.client.patch(ME_URL, update_payload, format='json')

        user = get_user_model().objects.get(email=payload["email"])
        adminProfile = AdminProfile.objects.get(email=payload["email"])

        self.assertEqual(adminProfile.firstName, update_payload["firstName"])
        self.assertTrue(user.check_password(update_payload["user"]["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
