"""
URL mapping for user profile API.
"""

from django.urls import path

from userProfile import views

app_name = "userProfile"

urlpatterns = [
	path('update-user-active-status/<int:pk>/', views.UpdateUserActiveStatusView.as_view(), name='update_user_active_status'),
	path('create/', views.UserProfileCreateView.as_view(), name="create"),
	path('get-all-users/', views.UserProfileGetView.as_view(), name="get"),
	path('me/', views.ManageUserProfileView.as_view(), name='me')
]
