"""
Test for the business profile APIs.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import BusinessProfile, Location

CREATE_BUSINESS_PROFILE_URL = reverse("businessProfile:create")
ME_URL = reverse("businessProfile:me")

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
	"businessName": "test business",
	"businessType": "test type",
	"businessLogo": "http://test-logo.jpg",
	"email": "test_user@example.com",
	"contactNo": "0039928",
	"websiteUrl": "http://test_website.com",
	"businessHours":{
        "monday": "10:00am-09:00pm",
        "tuesday": "10:00am-09:00pm",
        "wednesday": "10:00am-09:00pm",
        "thursday": "10:00am-09:00pm",
        "friday": "10:00am-09:00pm"
    }
}

update_payload = {
	"user": {
		"password": "test123"
	},
	"businessName": "Updated business",
	"businessLogo": "http://updated-logo.jpg",
	"contactNo": "1213456",
}

def create_business():
    """Create and return a new business Profile"""
    payload_copy = payload.copy()
    user_data = payload_copy.pop('user')
    location_data = payload_copy.pop('location')

    user = get_user_model().objects.create_user(**user_data, role="Business")
    location = Location.objects.create(**location_data)
    businessProfile = BusinessProfile.objects.create(user=user, location=location, **payload_copy)
    return businessProfile


class PublicUserApiTests(TestCase):
    """Test the public features of the admin profile API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_business_profile_successful(self):
        """Test creating a business is successful"""

        res = self.client.post(CREATE_BUSINESS_PROFILE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload["email"])
        businessProfile = BusinessProfile.objects.get(email=payload["email"])

        self.assertEqual(user.role, "Business")
        self.assertTrue(user.check_password(payload["user"]["password"]))
        self.assertEqual(businessProfile.businessName, payload["businessName"])
        self.assertNotIn("password", res.data)

    def test_user_with_email_exists_error(self):
        """Test error returns if business profile with email exists"""
        create_business();

        res = self.client.post(CREATE_BUSINESS_PROFILE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password is less than 5 chars."""
        payload_copy = payload.copy()
        payload_copy["user"]["password"] = '123'
        res = self.client.post(CREATE_BUSINESS_PROFILE_URL, payload_copy, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        business_exists = get_user_model().objects.filter(email=payload["email"]).exists()

        self.assertFalse(business_exists)

    def test_retrieve_business_unauthorized(self):
        """Test authentication is required for business profiles."""

        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.user = create_business()

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

    def test_update_business_profile(self):
        """Test updating the business profile for authenticated user."""

        res = self.client.patch(ME_URL, update_payload, format='json')

        user = get_user_model().objects.get(email=payload["email"])
        businessProfile = BusinessProfile.objects.get(email=payload["email"])

        self.assertEqual(businessProfile.businessName, update_payload["businessName"])
        self.assertTrue(user.check_password(update_payload["user"]["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
