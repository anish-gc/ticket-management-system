from django.urls import path

from accounts.views.account_role_mapping_views import (
    AccountRoleMappingCreateListApiView,
    AccountRoleMappingDetailsApiView,
)
from accounts.views.account_views import (
    AccountCreateListApiView,
    AccountDetailsApiView,
    AccountToggleApiView,
)
from accounts.views.menu_views import MenuDetailsApiView, MenuListCreateApiView
from accounts.views.role_menu_permission_mapping_views import (
    RoleMenuPermissionCreateListApiView,
    RoleMenuPermissionDetailsApiView,
)
from accounts.views.role_views import RoleCreateListApiView, RoleDetailsApiView
from accounts.views.account_menu_mapping_views import (
    AccountMenuMappingCreateListApiView,
    AccountMenuMappingDetailsApiView,
)

urlpatterns = [
    # account model
    path("accounts/", AccountCreateListApiView.as_view(), name="account-create-list"),
    path("account/<pk>/", AccountDetailsApiView.as_view(), name="account-details"),
    path("account/toggle/<pk>/", AccountToggleApiView.as_view(), name="account-toggle"),
    # role model
    path("roles/", RoleCreateListApiView.as_view(), name="role-create-list"),
    path("role/<pk>/", RoleDetailsApiView.as_view(), name="role-details"),
    # menu model
    path("menus/", MenuListCreateApiView.as_view(), name="menu-create-list"),
    path("menu/<pk>/", MenuDetailsApiView.as_view(), name="menu-details"),
    # mapping
    # account role mapping
    path(
        "account/role/mapping/",
        AccountRoleMappingCreateListApiView.as_view(),
        name="account-role-mapping-create-list",
    ),
    path(
        "account/role/mapping/<pk>/",
        AccountRoleMappingDetailsApiView.as_view(),
        name="account-role-mapping-detail",
    ),
    # role menu permission mapping
    path(
        "role/menu/permission/mapping/",
        RoleMenuPermissionCreateListApiView.as_view(),
        name="role-menu-permission-list",
    ),
    path(
        "role/menu/permission/mapping/",
        RoleMenuPermissionDetailsApiView.as_view(),
        name="role-menu-permission-detail",
    ),
    # account menu mapping
    path(
        "account/menu/mapping/",
        AccountMenuMappingCreateListApiView.as_view(),
        name="account-menu-mapping-create-list",
    ),
    path(
        "account/menu/mapping/<pk>/",
        AccountMenuMappingDetailsApiView.as_view(),
        name="account-menu-mapping-detail",
    ),
]
