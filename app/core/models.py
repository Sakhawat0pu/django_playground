"""
Database models.
"""

from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user"""
        if not email:
            raise ValueError("User must have an email address.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""

    USER = 'user'
    ADMIN = 'admin'
    BUSINESS = 'business'

    role_choices = [
        (USER, 'User'),
        (ADMIN, 'Admin'),
        (BUSINESS, 'Business')
    ]

    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    role = models.CharField(max_length=50, choices=role_choices, default=USER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"


class Location(models.Model):
    """Location objects"""
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.city + ', ' + self.state + ', ' + self.country

class UserProfile(models.Model):
    """Regular user profile objects"""
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'

    gender_choices = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other')
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='user_profile',
        on_delete=models.CASCADE
        )
    firstName = models.CharField(max_length=255)
    middleName = models.CharField(max_length=255, blank=True, null=True)
    lastName = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    gender = models.CharField(max_length=50, choices=gender_choices)
    dob = models.DateField()
    contactNo = models.CharField(max_length=50, null=True, blank=True)
    profileImg = models.CharField(max_length=255, null=True, blank=True)
    interests = ArrayField(models.CharField(max_length=100), blank=True)
    location = models.OneToOneField(Location, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def is_authenticated(self):
        return self.user.is_authenticated

    def __str__(self):
        return self.email


class AdminProfile(models.Model):
    """Admin profile objects"""
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'

    gender_choices = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other')
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='admin_profile',
        on_delete=models.CASCADE
        )
    firstName = models.CharField(max_length=255)
    middleName = models.CharField(max_length=255, blank=True, null=True)
    lastName = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    gender = models.CharField(max_length=50, choices=gender_choices)
    dob = models.DateField()
    contactNo = models.CharField(max_length=50, null=True, blank=True)
    profileImg = models.CharField(max_length=255, null=True, blank=True)
    interests = ArrayField(models.CharField(max_length=100), blank=True)
    location = models.OneToOneField(Location, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def is_authenticated(self):
        return self.user.is_authenticated

    def __str__(self):
        return self.email

class BusinessProfile(models.Model):
    """Business profile objects"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='business_profile',
        on_delete=models.CASCADE
        )
    businessName = models.CharField(max_length=255)
    businessType = models.CharField(max_length=255)
    businessHours = models.JSONField()
    email = models.EmailField(max_length=255, unique=True)
    contactNo = models.CharField(max_length=50)
    businessLogo = models.CharField(max_length=255, null=True, blank=True)
    websiteUrl = models.CharField(max_length=255, null=True, blank=True)
    location = models.OneToOneField(Location, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def is_authenticated(self):
        return self.user.is_authenticated

    def __str__(self):
        return self.email