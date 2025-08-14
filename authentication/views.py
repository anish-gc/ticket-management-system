import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication


from authentication.validation import confirm_login_details, login_validation
from utilities import global_parameters
from utilities.api_views import BaseAPIView
from utilities.exception import CustomAPIException
from utilities.jwt_authentication import CustomJWTAuthentication

logger = logging.getLogger(__name__)


class LoginApiView(APIView):
    """
    JWT-based login but keeps the same API style as the old token system.
    """
    authentication_classes = []  # No authentication needed for login
    permission_classes = []  # No permissions needed for login
    throttle_scope = "login"  # Rate limiting

    @method_decorator(never_cache)
    def post(self, request) -> Response:
        try:
            # Extract and validate credentials
            username, password = login_validation(request)

            # Authenticate using Django's built-in system
            user = authenticate(request, username=username, password=password)
            if not user:
                logger.warning(f"Login failed for username: {username}")
                return self._create_error_response(
                    global_parameters.NO_USER,
                    status_code=status.HTTP_401_UNAUTHORIZED
                )

           
            # Additional login details from your existing helper
            login_data = confirm_login_details(user)

            

            return self._create_success_response(
                login_data,
                global_parameters.RESPONSE_SUCCESS_MESSAGE
            )

        except CustomAPIException as exc:
            logger.error(f"Authentication error: {str(exc)}", exc_info=True)
            status_code = getattr(exc, "status_code", status.HTTP_401_UNAUTHORIZED)
            return self._create_error_response(str(exc), status_code)

        except Exception as exc:
            logger.error(f"Unexpected login error: {str(exc)}", exc_info=True)
            return self._create_error_response(
                global_parameters.NO_USER,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _create_success_response(self, data, message):
        response_data = {
            global_parameters.RESPONSE_CODE: global_parameters.SUCCESS_CODE,
            global_parameters.RESPONSE_MESSAGE: message,
            global_parameters.DATA: data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def _create_error_response(self, error_message, status_code=status.HTTP_401_UNAUTHORIZED):
        response_data = {
            global_parameters.RESPONSE_CODE: global_parameters.UNSUCCESS_CODE,
            global_parameters.RESPONSE_MESSAGE: global_parameters.INTERNAL_SERVER_ERROR,
            global_parameters.RESPONSE_MESSAGE: error_message,
        }
        return Response(response_data, status=status_code)


class LogoutApiView(BaseAPIView):
    """
    JWT-based logout that blacklists the refresh token.
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]
    required_permissions = []  

    @method_decorator(never_cache)
    def post(self, request) -> Response:
        try:
            refresh_token = request.data.get("refreshToken")
            if not refresh_token:
                return self.handle_validation_error("Refresh token is required for logout.")

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            return self.handle_success("You have been successfully logged out from this system.")

        except Exception as exc:
            logger.error(f"Unexpected error during logout: {str(exc)}", exc_info=True)
            return self.handle_view_exception(exc)
