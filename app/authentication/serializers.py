"""
Serializers for the auth APIs.
"""

from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext as _
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.exceptions import AuthenticationFailed

from rest_framework.authtoken.models import Token
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            msg = _("User does not exist")
            raise serializers.ValidationError(msg, code="invalid")

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )

        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _("Unable to authenticate with provided credentials")
            raise serializers.ValidationError(msg, code="authorization")

        token, created = Token.objects.get_or_create(user=user)

        attrs["user"] = user
        attrs["token"] = token

        return attrs


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ('old_password', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            msg=_("Password fields didn't match.")
            raise serializers.ValidationError(msg, code="invalid")

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            msg = _("Old password is not correct")
            raise serializers.ValidationError(msg, code="invalid")
        return value

    def update(self, instance, validated_data):

        instance.set_password(validated_data['password'])
        instance.save()

        return instance


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)



class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']
