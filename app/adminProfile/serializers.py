""""
Serializers for the admin profile APIs.
"""
from django.contrib.auth import get_user_model

from rest_framework import serializers
from django.utils.translation import gettext as _

from core.models import AdminProfile, Location

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut


class AdminActiveStatusSerializer(serializers.ModelSerializer):
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

class AdminProfileSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    user = UserSerializer()

    class Meta:
        model = AdminProfile
        exclude = ['createdAt', 'updatedAt']

    def create(self, validated_data):
        """Create and return a admin profile with encrypted password."""

        location_data = validated_data.pop('location')
        user_data = validated_data.pop('user')
        location_serializer = LocationSerializer(data=location_data)  # Pass location data through the serializer
        if location_serializer.is_valid():
            location = location_serializer.save()  # Save the location instance
            user = get_user_model().objects.create_user(**user_data)
            admin_profile = AdminProfile.objects.create(user=user, location=location, **validated_data)
            return admin_profile
        else:
            # Handle serializer validation errors
            raise serializers.ValidationError(_("Invalid location data"), code='Invalid')

    def update(self, instance, validated_data):
        """Update and return user profile"""
        location_data = validated_data.pop('location', None)
        admin_data = validated_data.pop('user', None)

        # Update UserProfile instance
        instance.firstName = validated_data.get('firstName', instance.firstName)
        instance.middleName = validated_data.get('middleName', instance.middleName)
        instance.lastName = validated_data.get('lastName', instance.lastName)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.dob = validated_data.get('dob', instance.dob)
        instance.contactNo = validated_data.get('contactNo', instance.contactNo)
        instance.profileImg = validated_data.get('profileImg', instance.profileImg)
        instance.interests = validated_data.get('interests', instance.interests)

        # Update Location instance
        if location_data:
            location_serializer = LocationSerializer(instance.location, data=location_data)
            if location_serializer.is_valid():
                location_serializer.save()

        # Update User instance
        if (admin_data):
            user = instance.user
            password = admin_data.pop('password', None)
            user.email = admin_data.get('email', user.email)
            if (password):
                user.set_password(password)
            user.save()

        # Save UserProfile instance
        instance.save()
        return instance
