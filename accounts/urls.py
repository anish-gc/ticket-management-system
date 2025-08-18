from django.urls import path

from accounts.views.account_role_mapping_views import AccountRoleMappingCreateListApiView, AccountRoleMappingDetailsApiView
from accounts.views.account_views import AccountCreateListApiView, AccountDetailsApiView, AccountToggleApiView
from accounts.views.menu_views import MenuDetailsApiView, MenuListCreateApiView
from accounts.views.role_menu_permission_views import RoleMenuPermissionCreateListApiView, RoleMenuPermissionDetailsApiView
from accounts.views.role_views import RoleCreateListApiView, RoleDetailsApiView
from accounts.views.user_menu_assignment_views import UserMenuAssignmentCreateListApiView, UserMenuAssignmentDetailsApiView

urlpatterns = [
    # account model
    path("accounts/", AccountCreateListApiView.as_view(), name="account-create-list"),
    path("account/<pk>/", AccountDetailsApiView.as_view(), name="account-details"),
    path("account/toggle/<pk>/", AccountToggleApiView.as_view(), name='account-toggle'),

    # role model
    path("roles/", RoleCreateListApiView.as_view(), name="role-create-list"),
    path("role/<pk>/", RoleDetailsApiView.as_view(), name="role-details"),
    # menu model
    path("menus/", MenuListCreateApiView.as_view(), name="menu-create-list"),
    path("menu/<pk>/", MenuDetailsApiView.as_view(), name="menu-details"),
    
    path("account/roles/mapping/", AccountRoleMappingCreateListApiView.as_view(), name='account-role-mapping-create-list'),
    path("account/role/mapping/<pk>/", AccountRoleMappingDetailsApiView.as_view(), name='account-role-mapping-detail'),


    path("role/menus/permission/", RoleMenuPermissionCreateListApiView.as_view(), name='role-menu-permission-list'),
    path("role/menu/permission/", RoleMenuPermissionDetailsApiView.as_view(), name='role-menu-permission-detail'),

    path("user-menu-assignments/", UserMenuAssignmentCreateListApiView.as_view(), name='user-menu-assignment-create-list'),
    path("user-menu-assignment/<pk>/", UserMenuAssignmentDetailsApiView.as_view(), name='user-menu-assignment-detail'),


]
