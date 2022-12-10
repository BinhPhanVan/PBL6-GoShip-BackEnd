from django.db import models

# Create your models here.
class Address(models.Model):
    address_notes = models.CharField(max_length= 255, null = True, blank=True, default="")
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    def __str__(self):
        return self.address_notes 
    class Meta:
        db_table = 'Address'


class Notification(models.Model):
    title = models.CharField(max_length=255 , null = True, blank=True)
    body = models.TextField(max_length=255, null = True, blank= True)
    list_choices = (
        (1, 'Có đơn hàng gần đây'),
        (2,'Tài xế đã nhận đơn hàng')
    )   
    type = models.IntegerField(choices= list_choices, null=True, blank=True)
