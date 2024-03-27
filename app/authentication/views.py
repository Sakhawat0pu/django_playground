"""
Views for auth APIs.
"""

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication


from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, smart_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail

from .serializers import AuthTokenSerializer, ChangePasswordSerializer, ForgotPasswordSerializer, ResetPasswordSerializer

class LoginView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class LogoutView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    """
    View to logout user by invalidating their authentication token.
    """
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            request.user.auth_token.delete()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "User is not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)

class ChangePasswordView(generics.UpdateAPIView):
    queryset = get_user_model().objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user



class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        user = get_user_model().objects.filter(email=email).first()
        if user:
            token = PasswordResetTokenGenerator().make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            print(token)
            print(urlsafe_base64_encode(force_bytes(token)))
            # Send email with password reset link
            reset_link = f"http://localhost:5000/reset-password?userId={uidb64}&token={urlsafe_base64_encode(force_bytes(token))}/"
            send_mail(
                'Reset Your Password',
                f'Please click the following link to reset your password: {reset_link}',
                'from@example.com',
                [email],
                fail_silently=False,
            )
            return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(generics.CreateAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']
        uidb64 = serializer.validated_data['uidb64']


        decoded_token = urlsafe_base64_decode(token).decode()
        try:
            uid = smart_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(id=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            user = None

        if user is not None and PasswordResetTokenGenerator().check_token(user, decoded_token):
            user.set_password(password)
            user.save()
            return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)


