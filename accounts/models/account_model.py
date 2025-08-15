

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


import logging

from accounts.account_manager import AccountManager
from accounts.models.role_model import Role
from utilities.models import BaseModel

logger = logging.getLogger(__name__)





class Account(AbstractBaseUser, BaseModel, PermissionsMixin):
    """
    Custom user account model that extends both AbstractBaseUser for authentication
    and BaseModel for common fields and behavior.
    """
    username = models.CharField(max_length=50,unique=True, blank=False, null=False,   help_text="Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only.")
    
    email = models.EmailField(unique=True,  blank=True, null=True, help_text="Optional email address. Must be unique if provided.")
    phone_number = models.CharField(max_length=10, unique=True,        help_text="Required. 10-digit phone number.")
    address = models.CharField(max_length=255, blank=True, help_text="Address of the user (e.g., Tilottama-3, Yogikuti, Shantichowk, near futsal Brahmapath)")  
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name='accounts', blank=True, null=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number', ]

    objects = AccountManager()
    
    def save(self, *args, **kwargs):
        if self.email == "":
            self.email = None  # Convert empty string to None to handle unique constraint
        
        super().save(*args, **kwargs)


    class Meta:
        db_table = "accounts"
        ordering = ['-created_at']

    def __str__(self):
        return self.username

  
  


    def user_designation(self):
        designation = 'staff'
        if self.is_superuser:
            designation = 'superUser'
        return designation    

