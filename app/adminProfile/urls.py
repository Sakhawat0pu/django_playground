"""
URL mapping for admin profile API.
"""

from django.urls import path

from adminProfile import views

app_name = "adminProfile"

urlpatterns = [
	path('update-admin-active-status/<int:pk>/', views.UpdateAdminActiveStatusView.as_view(), name='update_admin_active_status'),
	path('create/', views.AdminProfileCreateView.as_view(), name="create"),
	path('get-all-admins/', views.AdminProfileGetView.as_view(), name="get-all-admins"),
	path('me/', views.ManageAdminProfileView.as_view(), name='me')
]
