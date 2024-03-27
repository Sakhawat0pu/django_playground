"""
URL mapping for auth APIs.
"""

from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from authentication import views

app_name = "authentication"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("change-password/", views.ChangePasswordView.as_view(), name="changePassword"),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgotPassword'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='resetPassword'),
]
