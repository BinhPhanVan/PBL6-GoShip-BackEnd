from django.contrib import admin
from .models import Payment, Category, Status, Order
# Register your models here.
admin.site.register(Payment)
admin.site.register(Category)
admin.site.register(Status)
admin.site.register(Order)