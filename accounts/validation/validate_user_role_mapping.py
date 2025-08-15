from accounts.models.account_model import Account
from accounts.models.role_model import Role
from utilities.exception import CustomAPIException
from utilities.global_functions import model_validation


def prepare_user_role_updates(request):
    data = request.data

    # Early validation with specific error codes
    if not (user_list := data.get("userList", [])):
        raise CustomAPIException("User list cannot be blank.", code="empty_user_list")

    if not (role_id := data.get("roleId")):
        raise CustomAPIException("Role ID cannot be blank.", code="missing_role_id")

    # Get role with existence check
    role = model_validation(
        Role,
        "Selected role does not exist.",
        {"reference_id": role_id, "is_active": True},
    )

    # Fetch users and identify missing ones
    users = Account.objects.filter(reference_id__in=user_list, is_active=True)

    found_ids = {str(id) for id in users.values_list("reference_id", flat=True)}
    if missing_ids := set(user_list) - found_ids:
        raise CustomAPIException(
            f"Invalid or inactive users: {', '.join(missing_ids)}",
        )

    # Prepare updates
    for user in users:
        user.role = role

    return users  #
