"""
URL mapping for business profile API.
"""

from django.urls import path

from businessProfile import views

app_name = "businessProfile"

urlpatterns = [
	path('update-business-active-status/<int:pk>/', views.UpdateBusinessActiveStatusView.as_view(), name='update_business_active_status'),
	path('create/', views.BusinessProfileCreateView.as_view(), name="create"),
	path('get-all-business_profiles/', views.BusinessProfileGetView.as_view(), name="get-all-business_profiles"),
	path('me/', views.ManageBusinessProfileView.as_view(), name='me')
]
