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