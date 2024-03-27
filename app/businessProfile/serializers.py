""""
Serializers for the business profile APIs.
"""
from django.contrib.auth import get_user_model

from rest_framework import serializers
from django.utils.translation import gettext as _

from core.models import BusinessProfile, Location

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut


class BusinessActiveStatusSerializer(serializers.ModelSerializer):
    """Serializer for updating the is_active field of a user."""

    class Meta:
        model = get_user_model()
        fields = ["is_active"]

class LocationSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(read_only=True)
    longitude = serializers.FloatField(read_only=True)

    class Meta:
        model = Location
        fields = ['street','city', 'state', 'country', 'latitude', 'longitude']

    def create(self, validated_data):
        address = self._get_full_address(validated_data)
        latitude, longitude = self._get_latitude_longitude(address)
        validated_data['latitude'] = latitude
        validated_data['longitude'] = longitude
        return super().create(validated_data)

    def _get_full_address(self, validated_data):
        return f"{validated_data['street']}, {validated_data['city']}, {validated_data['state']}, {validated_data['country']}"

    def _get_latitude_longitude(self, address):
        geolocator = Nominatim(user_agent="geopy/1.0")
        try:
            location = geolocator.geocode(address)
            if location:
                return location.latitude, location.longitude
        except GeocoderTimedOut:
            pass
        return None, None

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password']
        extra_kwargs = {"password": {"write_only": True, "min_length": 6}}

class BusinessProfileSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    user = UserSerializer()
    businessHours = serializers.DictField()
    class Meta:
        model = BusinessProfile
        # exclude = ['createdAt', 'updatedAt']
        fields = ["user", "location", "businessName", "businessType", "businessHours", "email", "contactNo", "businessLogo", "websiteUrl",]

    def create(self, validated_data):
        """Create and return a business profile with encrypted password."""

        location_data = validated_data.pop('location')
        user_data = validated_data.pop('user')
        location_serializer = LocationSerializer(data=location_data)  # Pass location data through the serializer
        if location_serializer.is_valid():
            location = location_serializer.save()  # Save the location instance
            user = get_user_model().objects.create_user(**user_data)
            business_profile = BusinessProfile.objects.create(user=user, location=location, **validated_data)
            return business_profile
        else:
            # Handle serializer validation errors
            raise serializers.ValidationError(_("Invalid location data"), code='Invalid')

    def update(self, instance, validated_data):
        """Update and return user profile"""
        location_data = validated_data.pop('location', None)
        business_data = validated_data.pop('user', None)

        # Update UserProfile instance
        instance.businessName = validated_data.get('businessName', instance.businessName)
        instance.businessType = validated_data.get('businessType', instance.businessType)
        instance.businessLogo = validated_data.get('businessLogo', instance.businessLogo)
        instance.businessHours = validated_data.get('businessHours', instance.businessHours)
        instance.email = validated_data.get('email', instance.email)
        instance.contactNo = validated_data.get('contactNo', instance.contactNo)
        instance.websiteUrl = validated_data.get('websiteUrl', instance.websiteUrl)

        # Update Location instance
        if location_data:
            location_serializer = LocationSerializer(instance.location, data=location_data)
            if location_serializer.is_valid():
                location_serializer.save()

        # Update User instance
        if (business_data):
            user = instance.user
            password = business_data.pop('password', None)
            user.email = business_data.get('email', user.email)
            if (password):
                user.set_password(password)
            user.save()

        # Save UserProfile instance
        instance.save()
        return instance
