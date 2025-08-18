"""This module used fot login and register login will be done through custom authetication."""

import logging
from datetime import datetime

from django.db.models import F, Value as V
from django.db.models.functions import Concat

from accounts.models.account_model import Account
from accounts.serializers.account_serializer import (
    AccountListSerializer,
    AccountSerializer,
)
from utilities.api_views import BaseAPIView


logger = logging.getLogger("django")


class AccountCreateListApiView(BaseAPIView):
    """
    Retrieves a list of all active users. This view requires custom authentication and permissions.
    """

    menu_url = "/accounts/"

    def get(self, request):

        account_data = self.get_serializer_data(
            Account, 
            AccountListSerializer, 
            request=self.request,  
            paginate=True,  # Enable pagination
            is_active=True
        )   
        tickets_data = self.get_menu_tickets()
        return self.handle_success({
            "account_data": account_data,
            "ticketsData": tickets_data
        })

    def post(self, request):
        """Create a new User."""
        serializer = AccountSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            account = serializer.save(created_by=request.user, created_at=datetime.now())
            account.set_password(self.request.data['password'])

            return self.handle_success("Account created successfully.")
        return self.handle_invalid_serializer(serializer)


class AccountDetailsApiView(BaseAPIView):
    """API endpoint for retrieving, updating, and deleting a specific account."""

    menu_url = "/accounts/"

    def get(self, request, pk):
        """Retrieve a account by reference_id."""
        return self.handle_serializer_data(
            Account, AccountListSerializer, False, reference_id=pk
        )

    def patch(self, request, pk):
        """Update a account."""
        account = Account.objects.get(reference_id=pk)

        serializer = AccountSerializer(
            account, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(updated_by=request.user, updated_at=datetime.now())
            return self.handle_success("Account updated successfully.")
        return self.handle_invalid_serializer(serializer)

    def delete(self, request, pk):
        """Delete a account."""
        try:
            account = Account.objects.get(reference_id=pk)
            account.delete()
            return self.handle_success("Account deleted successfully.")
        except Exception as exe:
            return self.handle_view_exception(exe)


        
class AccountToggleApiView(BaseAPIView):
    """
    Toggle the account.
    """
    menu_url = '/activate/account/'
    action = 'U'

    def patch(self, request, pk):
        try:
            instance = Account.objects.get(reference_id=pk)
            instance.is_active = not instance.is_active  # Toggle is_active status
            instance.updated_by = request.user
            instance.updated_at = datetime.now()
            instance.save()

            message = 'Account is activated successfully.' if instance.is_active else 'Account is deactivated successfully.'
            return self.handle_success(message)

        except Exception as exe:
            return self.handle_view_exception(exe)
        