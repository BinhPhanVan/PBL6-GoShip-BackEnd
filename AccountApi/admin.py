from django.contrib import admin
from .models import Account
from UserApi.models import *
# Register your models here. 

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display= ('phone_number','name', 'role', 'created_at', 'updated_at')
    list_filter = ("role",)
    def name(self, obj):
        res = []
        if obj.role == 1:
            res.append(Customer.objects.filter(account=obj).first().name)
        elif obj.role ==2:
            res.append(Shipper.objects.filter(account=obj).first().name)
        else:
            res.append('Admin')
        return res