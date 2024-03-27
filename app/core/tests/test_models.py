"""
Test for models.
"""

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelsTest(TestCase):
    """Test Models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with email is successful"""
        username = "test username2"
        email = "test@example.com"
        password = "testPass123"
        user = get_user_model().objects.create_user(username=username, email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users"""

        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.com", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
            ["test5@example.Com", "test5@example.com"],
        ]

        username = ["username1", "username2", "username3", "username4", "username5"]
        i = 0
        for email, expected_email in sample_emails:
            user = get_user_model().objects.create_user(
                email=email, password="sample123", username= username[i]
            )
            i += 1
            self.assertEqual(user.email, expected_email)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a value error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123")

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser("test@example.com", "test123")

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

