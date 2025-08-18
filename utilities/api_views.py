import logging


from rest_framework.views import APIView

from accounts.models.menu_model import Menu
from tickets.models.ticket_model import Ticket
from tickets.serializers.ticket_serializer import TicketListSerializer
from tickets.ticket_manager import TicketFilterManager
from utilities.custom_response import HandleResponseMixin
from utilities.jwt_authentication import CustomJWTAuthentication
from utilities.permission import CustomPermission, EnhancedCustomPermission 

logger = logging.getLogger("django")



class BaseAPIView(APIView, HandleResponseMixin):
    """
    Base class for API views.
    """
    menu_url = ""  
    action = ""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [EnhancedCustomPermission]

    def get_menu_tickets(self, **filter_kwargs):
        """
        Return tickets related to this view's menu_url with optional filtering
        
        Args:
            **filter_kwargs: Additional filtering parameters for TicketFilterManager
        """
        if not self.menu_url:
            return []

        try:
            from accounts.models import Menu
            menu = Menu.objects.get(menu_url=self.menu_url)
            tickets = TicketFilterManager.get_filtered_tickets(
                menu=menu,
                **filter_kwargs
            )
            return TicketListSerializer(tickets, many=True).data
        except Menu.DoesNotExist:
            return []
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

