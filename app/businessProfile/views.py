"""
Views for the business profile APIs.
"""

from rest_framework import generics, permissions, authentication

from django.contrib.auth import get_user_model

from businessProfile.serializers import (
	BusinessActiveStatusSerializer,
	BusinessProfileSerializer
)

from core.models import BusinessProfile

class UpdateBusinessActiveStatusView(generics.UpdateAPIView):
    """API endpoint to update the is_active field of a business."""

    queryset = get_user_model().objects.all()
    serializer_class = BusinessActiveStatusSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_update(self, serializer):
        serializer.save()

class BusinessProfileCreateView(generics.CreateAPIView):
    serializer_class = BusinessProfileSerializer

class BusinessProfileGetView(generics.ListAPIView):
    """Only admin can see the list of business profiles."""
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileSerializer
    permission_classes = [permissions.IsAdminUser]

class ManageBusinessProfileView(generics.RetrieveUpdateDestroyAPIView):
    """Manage the authenticated business profiles."""

    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated business profiles."""
        return self.request.user.business_profile