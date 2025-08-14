from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
import logging

from utilities import global_parameters
logger = logging.getLogger("__name__")


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that:
    1. Integrates with your existing user model
    """
    def authenticate(self, request):
        try:
            # Get the raw token from the header
            header = self.get_header(request)
            print(header)
            if header is None:
                return None

            raw_token = self.get_raw_token(header)
            if raw_token is None:
                return None
            # Validate and decode the token
            validated_token = self.get_validated_token(raw_token)
            
            # Get the user from the token
            user = self.get_user(validated_token)
         
          
            return (user, validated_token)
            
        except InvalidToken as e:
            raise AuthenticationFailed(str(e))
        except Exception as ex:
            logger.exception(f"Unexpected error during JWT authentication: {str(ex)}")
            raise AuthenticationFailed(global_parameters.NO_USER, code=401)
    
   