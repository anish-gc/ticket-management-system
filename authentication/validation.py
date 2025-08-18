import base64
import logging
from typing import Dict, Tuple, Any

from django.conf import settings
from django.http import HttpRequest
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.build_menu import get_menu_structure
from accounts.models import Account
from utilities.exception import AuthenticationFailedError, CustomAPIException

logger = logging.getLogger("django")


def login_validation(request: HttpRequest) -> Tuple[str, str]:
    """
    Extract and validate Basic Auth credentials from request.

    Returns:
        (username, password)
    """
    try:
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            raise AuthenticationFailedError("Authorization header missing")

        parts = auth_header.split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "basic":
            raise AuthenticationFailedError("Invalid authentication type")

        try:
            decoded = base64.b64decode(parts[1]).decode("utf-8")
        except Exception:
            raise AuthenticationFailedError("Invalid authorization encoding")

        if ":" not in decoded:
            raise AuthenticationFailedError("Invalid credentials format")

        username, password = decoded.split(":", 1)

        if not username or not password:
            raise AuthenticationFailedError("Username and password cannot be empty")
        return username, password

    except AuthenticationFailedError as exc:
        raise CustomAPIException(exc)
    except Exception as e:
        logger.error(f"Login validation error: {str(e)}", exc_info=True)
        raise AuthenticationFailedError("Invalid credentials")


def confirm_login_details(user: Account) -> Dict[str, Any]:
    """
    Generate JWT tokens for the authenticated user and return old-style response format.
    """
    try:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        auth_data = {
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "username": user.username,
            "designation": "superadmin" if user.is_superuser else user.role.name,
            "sessionTimeInMinutes": settings.SIMPLE_JWT.get(
                "ACCESS_TOKEN_LIFETIME"
            ).total_seconds()
            / 60,
            "menu": (
                get_menu_structure(None, is_superuser=True)
                if user.is_superuser
                else get_menu_structure(user.role.id, is_superuser=False, user_id=user.id)
            ),
        }
        return auth_data
    except CustomAPIException as exc:
        raise CustomAPIException(exc)
    except Exception as e:
        logger.error(f"Login confirmation failed: {str(e)}", exc_info=True)
        raise AuthenticationFailedError("Login processing failed")


def invalidate_user_session(refresh_token: str) -> None:
    """
    Blacklist a refresh token to effectively log out the user.
    """
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        logger.info("Refresh token blacklisted successfully")
    except Exception as e:
        logger.error(f"Failed to blacklist token: {str(e)}")
        raise AuthenticationFailedError("Invalid or expired refresh token")
