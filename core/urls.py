from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from authentication.views import LoginApiView, LogoutApiView

urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("api/auth/login/", LoginApiView.as_view(), name="login"),
    path("api/auth/logout/", LogoutApiView.as_view(), name="logout"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # accounts
    path("api/", include("accounts.urls")),
    path("api/", include("tickets.urls"))
]
