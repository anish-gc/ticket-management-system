"""
This module provides API views for managing menu items within the application.
Classes:
- MenuListApiView: Handles listing and creation of menu items.
- MenuDetailsApiView: Handles retrieval, update and deletion of specific menu items.
"""

import logging
from datetime import datetime

from accounts.models.menu_model import Menu
from utilities.api_views import BaseAPIView
from accounts.serializers.menu_serializer import MenuListSerializer, MenuSerializer

logger = logging.getLogger("django")


def build_group_hierarchy(**query):
    all_menus = Menu.objects.filter(**query).order_by('display_order')
    parent_groups = all_menus.filter(parent_id__isnull=True)

    def build_hierarchy(parent_groups, all_menus):
        hierarchy = []
        for parent in parent_groups:
            children = all_menus.filter(parent_id=parent.id)
            child_hierarchy = build_hierarchy(children, all_menus)
            hierarchy.append({
                "referenceId": parent.reference_id,
                "Name": parent.menu_name,
                "subMenus": child_hierarchy if child_hierarchy else None 
            })
        return hierarchy

    return build_hierarchy(parent_groups, all_menus)


class MenuListCreateApiView(BaseAPIView):
    """
    API endpoint for listing and creating menu items.
    """
    menu_url = "/menu/" 
    action = "L" 

    def get(self, request):
        """Retrieve all menu items in hierarchical structure."""
        try:
            menus = build_group_hierarchy(is_active=True)
            data = {"menus": menus}
            return self.handle_success(None, data)
        except Exception as exe:
            return self.handle_view_exception(exe)

    def post(self, request):
        """Create a new menu item."""
        serializer = MenuSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(created_by=request.user, created_at=datetime.now())
            return self.handle_success("Menu created successfully.")
        return self.handle_invalid_serializer(serializer)


class MenuDetailsApiView(BaseAPIView):
    """
    API endpoint for retrieving, updating and deleting specific menu items.
    """
    menu_url = "/menu/"
    action = "L"

    def get(self, request, pk):
        """Retrieve a menu item by reference_id."""
        return self.handle_serializer_data(
            Menu, MenuListSerializer, False, reference_id=pk
        )

    def patch(self, request, pk):
        """Update a menu item."""
        menu = Menu.objects.get(reference_id=pk)
        serializer = MenuSerializer(
            menu, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(updated_by=request.user, updated_at=datetime.now())
            return self.handle_success("Menu updated successfully.")
        return self.handle_invalid_serializer(serializer)

    def delete(self, request, pk):
        """Delete a menu item."""
        try:
            menu = Menu.objects.get(reference_id=pk)
            menu.delete()
            return self.handle_success("Menu deleted successfully.")
        except Exception as exe:
            return self.handle_view_exception(exe)