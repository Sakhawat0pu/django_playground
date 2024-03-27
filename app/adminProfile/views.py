"""
Views for the admin profile APIs.
"""

from rest_framework import generics, permissions, authentication

from django.contrib.auth import get_user_model

from adminProfile.serializers import (
	AdminActiveStatusSerializer,
	AdminProfileSerializer
)

from core.models import AdminProfile

class UpdateAdminActiveStatusView(generics.UpdateAPIView):
    """API endpoint to update the is_active field of a admin."""

    queryset = get_user_model().objects.all()
    serializer_class = AdminActiveStatusSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_update(self, serializer):
        serializer.save()

class AdminProfileCreateView(generics.CreateAPIView):
    serializer_class = AdminProfileSerializer

class AdminProfileGetView(generics.ListAPIView):
    """Only admin can see the list of admins."""
    queryset = AdminProfile.objects.all()
    serializer_class = AdminProfileSerializer
    permission_classes = [permissions.IsAdminUser]

class ManageAdminProfileView(generics.RetrieveUpdateDestroyAPIView):
    """Manage the authenticated admin."""

    queryset = AdminProfile.objects.all()
    serializer_class = AdminProfileSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated admins"""
        return self.request.user.admin_profile