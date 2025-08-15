from django.contrib.auth.models import  BaseUserManager

from accounts.models.role_model import Role

class AccountManager(BaseUserManager):
    """Custom manager for Account model."""
    
    def create_user(self, username, phone_number, password=None, **extra_fields):
        if not username:
            raise ValueError("Username must be provided")
        if not phone_number:
            raise ValueError("Phone number must be provided")
        
        user = self.model(username=username, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
  

        return self.create_user(username, phone_number, password, **extra_fields)
