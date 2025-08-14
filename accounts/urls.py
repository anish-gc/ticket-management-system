from django.urls import path

from accounts.views.role_views import RoleCreateListApiView, RoleDetailsApiView

urlpatterns = [
    path("roles/", RoleCreateListApiView.as_view(), name="role-create-list"),
    path("role/<pk>/", RoleDetailsApiView.as_view(), name="role-details"),
]
