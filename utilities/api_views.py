import logging


from rest_framework.views import APIView

from utilities.custom_response import HandleResponseMixin
from utilities.jwt_authentication import CustomJWTAuthentication
from utilities.permission import CustomPermission 

logger = logging.getLogger("django")



class BaseAPIView(APIView, HandleResponseMixin):
    """
    Base class for API views.
    """
    menu_url = ""  
    action = ""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [CustomPermission]

    def initialize_action(self, method):
        """
        Dynamically set the action attribute based on the HTTP method.
        """
        method_action_mapping = {
            'GET': 'L',    # List or Retrieve
            'POST': 'C',   # Create
            'PATCH': 'U',  # Update
            'PUT': 'U',  # Update
            'DELETE': 'D', # Delete
        }
        self.action = method_action_mapping.get(method, '')

    def dispatch(self, request, *args, **kwargs):
        # Initialize action before processing the request
        self.initialize_action(request.method)
        return super().dispatch(request, *args, **kwargs)

