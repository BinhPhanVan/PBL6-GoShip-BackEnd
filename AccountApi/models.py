from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(
        self, phone_number, password=None,role = 1 , is_staff=False, is_superuser=False, is_active=True
    ):
        from UserApi.models import Admin
        if not phone_number:
            raise ValueError("User must have an phone_number address")
        if not password:
            raise ValueError("User must have an password")
        user_obj = self.model(phone_number=phone_number)
        user_obj.set_password(password)
        user_obj.is_staff = is_staff
        user_obj.is_superuser = is_superuser
        user_obj.is_active = is_active
        user_obj.role = role
        user_obj.save(using=self._db)
        return user_obj
    
    def create_staff(self, email, password=None):
        user_obj = self.create_user(email, password=password, is_staff=True)
        return user_obj
    
    def create_superuser(self, phone_number, password, **extra_fields):
        from UserApi.models import Admin
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        role = 3
        account= self.create_user(phone_number, password,role = role, **extra_fields)
        admin =  Admin(account = account)
        admin.save()
        return account
    

class Account(AbstractBaseUser, PermissionsMixin):
    list_roles = (
        (1, 'User'),
        (2, 'Shipper'),
        (3, 'Admin')
    )
    phone_number = models.CharField(max_length=12, null =False, unique= True)
    role = models.IntegerField(default=0, choices=list_roles)
    token_device = models.CharField(max_length=255, null= True, blank=True)
    created_at = models.DateTimeField(db_index=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_index=True, auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    class Meta:
        db_table = 'Account'
        ordering = ['created_at']

    def __str__(self):
        return self.phone_number
    
