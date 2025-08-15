from accounts.models.account_model import Account
from accounts.models.role_model import Role
from utilities.exception import CustomAPIException
from utilities.global_functions import model_validation


def validate_user_role_mapping(request):
    try:
        data = request.data
        users_to_update = []

        user_list = data.get("userList", [])
        if not user_list:
            raise CustomAPIException("User can not blank.")

        role_id = data.get("roleId")
        if not role_id:
            raise CustomAPIException("Role can not blank.")

        role = model_validation(Role, "Select a valid role.", {"reference_id": role_id})

        for user in user_list:
            user = model_validation(
                Account,
                "Select a valid user.",
                {"reference_id": user, "is_active": True},
            )
            user.role = role
            users_to_update.append(user)

        return users_to_update

    except CustomAPIException as exe:
        raise CustomAPIException(exe.detail)
    except Exception as exe:
        raise Exception(exe)
