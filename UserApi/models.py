from django.db import models
from AccountApi.models import Account
from BaseApi.models import Address
# Create your models here.
class Customer(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100, default = 'User')
    list_gender=(
        (0,'None'),
        (1,'Male'),
        (2,'Female')
    )
    gender = models.IntegerField(default=0, choices=list_gender)
    address = models.OneToOneField(Address, related_name='Address', on_delete=models.CASCADE, null =True)
    avatar_url = models.CharField(null= True, max_length=255, blank=True)
    birth_date = models.DateField(null= True, blank=True)
    distance_view= models.IntegerField(default=10)
    class Meta:
        db_table = 'Customer'

    def __str__(self):
        return self.name

        
class Shipper(models.Model):
    account = models.OneToOneField(
        Account, 
        on_delete=models.CASCADE, 
        primary_key=True)
    name = models.CharField(max_length=100, default = 'User')
    list_gender=(
        (0,'None'),
        (1,'Male'),
        (2,'Female')
    )
    gender = models.IntegerField(default=0, choices=list_gender)
    avatar_url = models.CharField(null= True, max_length=255, blank=True)
    birth_date = models.DateField(null= True, blank=True)
    address = models.OneToOneField(
        Address, 
        on_delete=models.CASCADE,
        null =True,
        )
    list_confirmed =(
        (0,'UnConfirm'),
        (1,'Confirming'),
        (2,'Confirmed'),
        (-1,'Deny')
    ) 
    url_identification_top = models.CharField(max_length=255,null=True)
    url_identification_back = models.CharField(max_length=255,null =True)
    identification_info = models.TextField(max_length=500, null=True, blank =True)
    url_face_video = models.CharField(max_length=255,null = True)
    confirmed = models.IntegerField(default=0, choices=list_confirmed)
    distance_receive= models.IntegerField(default=10)
    class Meta:
        db_table = 'Shipper'

    def __str__(self):
        return self.name

class Admin(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100, default = 'Admin')
    list_gender=(
        (0,'None'),
        (1,'Male'),
        (2,'Female')
    )
    gender = models.IntegerField(default=0, choices=list_gender)
    birth_date = models.DateField(null= True, blank=True)
    class Meta:
        db_table = 'Admin'

    def __str__(self):
        return self.name