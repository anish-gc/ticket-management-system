from rest_framework import serializers
from datetime import datetime
from accounts.models.menu_model import Menu
from utilities import global_parameters
from django.db import transaction


class MenuSerializer(serializers.Serializer):
    referenceId = serializers.CharField(source="reference_id", read_only=True)
    menuName = serializers.CharField(
        source="menu_name",
        max_length=200,
        error_messages={"required": "Menu name cannot be blank."},
    )
    menuUrl = serializers.CharField(
        source="menu_url",
        max_length=200,
        error_messages={"required": "Menu URL cannot be blank."},
    )
    createUrl = serializers.CharField(
        source="create_url",
        max_length=200,
        required=False,
        allow_blank=True,
        error_messages={"required": "Create URL cannot be blank."},
    )
    listUrl = serializers.CharField(
        source="list_url",
        max_length=200,
        required=False,
        allow_blank=True,
        error_messages={"required": "List URL cannot be blank."},
    )
    parentReferenceId = serializers.CharField(
        source="parent_reference_id", required=False, allow_blank=True, allow_null=True
    )
    icon = serializers.CharField(
        max_length=100, required=False, allow_blank=True, allow_null=True
    )
    visibility = serializers.BooleanField(required=False, default=True)
    displayOrder = serializers.IntegerField(
        source="display_order", required=False, default=0
    )
    depth = serializers.IntegerField(read_only=True)

    def _calculate_depth(self, parent):
        """Calculate the depth of a menu item based on its parent hierarchy."""
        if not parent:
            return 0

        depth = 0
        current = parent
        visited = set()  # Prevent infinite loops in case of circular references

        while current and current.id not in visited:
            visited.add(current.id)
            depth += 1
            current = current.parent

        return depth

    def _get_parent_instance(self, parent_reference_id):
        """Get parent instance from reference_id with validation."""
        if not parent_reference_id:
            return None

        try:
            return Menu.objects.get(reference_id=parent_reference_id)
        except Menu.DoesNotExist:
            raise serializers.ValidationError(
                {
                    global_parameters.ERROR_DETAILS: [
                        f"Parent menu with reference ID '{parent_reference_id}' does not exist."
                    ]
                }
            )

    @transaction.atomic
    def create(self, validated_data):
        """Create a new menu item with calculated depth."""
        parent_reference_id = validated_data.pop("parent_reference_id", None)
        parent = self._get_parent_instance(parent_reference_id)

        depth = self._calculate_depth(parent)

        menu = Menu.objects.create(parent=parent, depth=depth, **validated_data)
        return menu

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update menu item and recalculate depth if parent changes."""
        parent_reference_id = validated_data.pop("parent_reference_id", None)

        # Handle parent change
        if "parent_reference_id" in self.initial_data:
            new_parent = self._get_parent_instance(parent_reference_id)

            # Prevent circular reference
            if new_parent and self._would_create_circular_reference(
                instance, new_parent
            ):
                raise serializers.ValidationError(
                    {
                        global_parameters.ERROR_DETAILS: [
                            "Cannot set parent: this would create a circular reference."
                        ]
                    }
                )

            instance.parent = new_parent
            instance.depth = self._calculate_depth(new_parent)

            # Update depths of all descendants
            self._update_descendant_depths(instance)

        # Update other fields
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def _would_create_circular_reference(self, instance, new_parent):
        """Check if setting new_parent would create a circular reference."""
        if not new_parent:
            return False

        current = new_parent
        visited = set()

        while current and current.id not in visited:
            if current.id == instance.id:
                return True
            visited.add(current.id)
            current = current.parent

        return False

    def _update_descendant_depths(self, instance):
        """Recursively update depths of all descendant menus."""
        children = Menu.objects.filter(parent=instance)

        for child in children:
            child.depth = self._calculate_depth(instance) + 1
            child.save(update_fields=["depth"])
            self._update_descendant_depths(child)

    def validate(self, data):
        """Comprehensive validation for menu data."""
        menu_name = data.get("menu_name")
        parent_reference_id = data.get("parent_reference_id")

        # Validate menu name uniqueness (case-insensitive)
        if menu_name:
            qs = Menu.objects.filter(menu_name__iexact=menu_name)
            if self.instance:
                qs = qs.exclude(reference_id=self.instance.reference_id)
            if qs.exists():
                raise serializers.ValidationError(
                    {
                        global_parameters.ERROR_DETAILS: [
                            f"Menu with name '{menu_name}' already exists."
                        ]
                    }
                )

        # Validate parent exists (if provided)
        if parent_reference_id:
            parent = self._get_parent_instance(parent_reference_id)
            # Prevent self-referencing
            if self.instance and parent.reference_id == self.instance.reference_id:
                raise serializers.ValidationError(
                    {
                        global_parameters.ERROR_DETAILS: [
                            "A menu cannot be its own parent."
                        ]
                    }
                )

        return data

    def validate_menuUrl(self, value):
        """Validate menu URL format."""
        parent = self.initial_data.get("parentReferenceId") 
        print(parent)
        if parent and value and not value.startswith("/"):
            raise serializers.ValidationError("Sub Menu URL should start with '/'")
        return value

    def validate_displayOrder(self, value):
        """Validate display order is non-negative."""
        if value is not None and value < 0:
            raise serializers.ValidationError("Display order must be non-negative")
        return value


class MenuListSerializer(serializers.ModelSerializer):
    """Serializer for listing menus with read-only fields."""

    referenceId = serializers.CharField(source="reference_id", read_only=True)
    menuName = serializers.CharField(source="menu_name", read_only=True)
    menuUrl = serializers.CharField(source="menu_url", read_only=True)
    createUrl = serializers.CharField(source="create_url", read_only=True)
    listUrl = serializers.CharField(source="list_url", read_only=True)
    parentId = serializers.CharField(source="parent.reference_id", read_only=True)
    parentName = serializers.CharField(source="parent.menu_name", read_only=True)
    icon = serializers.CharField(read_only=True)
    visibility = serializers.BooleanField(read_only=True)
    displayOrder = serializers.IntegerField(source="display_order", read_only=True)
    depth = serializers.IntegerField(read_only=True)
    hasChildren = serializers.SerializerMethodField()
    fullPath = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = [
            "referenceId",
            "menuName",
            "menuUrl",
            "createUrl",
            "listUrl",
            "parentId",
            "parentName",
            "icon",
            "visibility",
            "displayOrder",
            "depth",
            "hasChildren",
            "fullPath",
        ]

    def get_hasChildren(self, obj):
        """Check if this menu has any active children."""
        return obj.children.filter(is_active=True).exists()

    def get_fullPath(self, obj):
        """Generate full hierarchical path for the menu."""
        path = []
        current = obj
        visited = set()  # Prevent infinite loops

        while current and current.id not in visited:
            path.append(current.menu_name)
            visited.add(current.id)
            current = current.parent

        return " > ".join(reversed(path))

    def to_representation(self, instance):
        """Customize output representation."""
        data = super().to_representation(instance)

        # Add computed fields
        data["displayLabel"] = f"{'  ' * data['depth']}{data['menuName']}"
        data["isRoot"] = data["depth"] == 0
        data["level"] = f"Level {data['depth'] + 1}"

        # Clean up None values
        for key, value in data.items():
            if value is None:
                data[key] = ""

        return data
