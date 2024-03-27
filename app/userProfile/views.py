"""
Views for the user profile APIs.
"""

from rest_framework import generics, permissions, authentication

from django.contrib.auth import get_user_model

from userProfile.serializers import (
	UserActiveStatusSerializer,
	UserProfileSerializer
)

from core.models import UserProfile

class UpdateUserActiveStatusView(generics.UpdateAPIView):
    """API endpoint to update the is_active field of a user."""

    queryset = get_user_model().objects.all()
    serializer_class = UserActiveStatusSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_update(self, serializer):
        serializer.save()

class UserProfileCreateView(generics.CreateAPIView):
    serializer_class = UserProfileSerializer

class UserProfileGetView(generics.ListAPIView):
    """Only admin can see the list of users."""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAdminUser]

class ManageUserProfileView(generics.RetrieveUpdateDestroyAPIView):
    """Manage the authenticated user."""

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user"""
        return self.request.user.user_profile