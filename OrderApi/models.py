from django.db import models

# Create your models here.
from django.db import models
from UserApi.models import Customer, Shipper
from BaseApi.models import Address
# Create your models here.

class Payment(models.Model):
    type = models.CharField(max_length=255, null = True)
    description = models.CharField(max_length=255, null = True, blank=True)
    class Meta:
        db_table = 'Payment'

    def __str__(self):
        return self.type


class Category(models.Model):
    name = models.CharField(max_length=255, null = True)
    is_protected = models.BooleanField(default=False)
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Category'

class Status(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null = True, blank=True)
    def __str__(self):
        return self.title
    class Meta:
        db_table = 'Status'

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    shipper = models.ForeignKey(Shipper,  on_delete=models.CASCADE, blank=True, null=True) #null = True
    payment =  models.ForeignKey(Payment, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000, null = True, blank=True)
    cost = models.BigIntegerField(null = True)
    distance = models.FloatField(null = True)
    category =  models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(db_index=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_index=True, auto_now=True)
    customer_notes = models.TextField(max_length=255, null=True, blank=True)
    address_start = models.OneToOneField(Address, on_delete=models.CASCADE, related_name='address_start')
    address_end = models.OneToOneField(Address,  on_delete=models.CASCADE, related_name='address_end')
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    img_order = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return 'Đơn yêu cầu giao hàng số ' +str(self.id)