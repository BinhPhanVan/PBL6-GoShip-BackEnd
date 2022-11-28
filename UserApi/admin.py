from django.contrib import admin
from .models import Customer, Shipper, Admin
# Register your models here.
admin.site.register(Customer)
admin.site.register(Shipper)
admin.site.register(Admin)